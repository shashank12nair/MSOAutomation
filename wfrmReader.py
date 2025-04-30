import struct
import numpy as np
import os
import plotly.graph_objects as go

def convert_wfm_to_npz(input_folder, show_plot=False):
    # Prepare output folder
    output_folder = os.path.join(input_folder, "converted_npz")
    os.makedirs(output_folder, exist_ok=True)

    # List all .wfm files
    wfm_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".wfm")]
    if not wfm_files:
        print("No .wfm files found in the specified directory.")
        return

    for wfm_file in wfm_files:
        filename = os.path.join(input_folder, wfm_file)
        file_wfm = os.path.splitext(wfm_file)[0]
        file_npz = os.path.join(output_folder, file_wfm + ".npz")

        try:
            file_size = os.path.getsize(filename)

            with open(filename, "rb") as bfile:
                bfile.seek(0x00)
                pCode = struct.unpack('H', bfile.read(2))
                vNumber = bfile.read(8)
                ndbc = struct.unpack('c', bfile.read(1))
                nbEOF = struct.unpack('i', bfile.read(4))
                nbPt = struct.unpack('c', bfile.read(1))
                bOffset1 = struct.unpack('i', bfile.read(4))

                if bOffset1[0] >= file_size:
                    print(f"[ERROR] Curve buffer offset in {wfm_file} exceeds file size. Skipping.")
                    continue

                bfile.seek(0x1e8)
                time_step = struct.unpack('d', bfile.read(8))

                bfile.seek(0x1f0)
                horZoomP = struct.unpack('d', bfile.read(8))

                bfile.seek(0x0a8)
                verScaF = struct.unpack('d', bfile.read(8))

                bfile.seek(0x0b0)
                verZoomP = struct.unpack('d', bfile.read(8))

                bfile.seek(0x0bc)
                explicit_dim_units = bfile.read(20).decode('utf-8', errors='ignore').strip('\x00')

                bfile.seek(0x1fc)
                implicit_dim_units = bfile.read(20).decode('utf-8', errors='ignore').strip('\x00')

                bfile.seek(bOffset1[0])
                time_values = []
                voltage_values = []
                point_index = 0

                while bfile.tell() < file_size:
                    raw_data = bfile.read(2)
                    if len(raw_data) < 2:
                        break
                    v = struct.unpack('h', raw_data)
                    voltage_values.append((v[0] * verScaF[0]) + verZoomP[0])
                    time_values.append(point_index * time_step[0] + horZoomP[0])
                    point_index += 1

                time_values = np.array(time_values, dtype=float)
                voltage_values = np.array(voltage_values, dtype=float)

                np.savez(
                    file_npz,
                    time=time_values,
                    voltage=voltage_values,
                    time_step=time_step[0],
                    horZoomP=horZoomP[0],
                    verScaF=verScaF[0],
                    verZoomP=verZoomP[0],
                    waveform_label=file_wfm,
                    explicit_dim_units=explicit_dim_units,
                    implicit_dim_units=implicit_dim_units
                )

                print(f"[OK] {wfm_file} -> {file_npz}")

                if show_plot:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=time_values, y=voltage_values, mode='lines', name=file_wfm))
                    fig.update_layout(title=file_wfm, xaxis_title="Time", yaxis_title="Voltage", template="plotly_dark")
                    fig.show()

        except Exception as e:
            print(f"[ERROR] Failed to process {wfm_file}: {e}")

# if __name__ == "__main__":
#     folder = input("Enter the path to the folder containing .wfm files: ").strip('"')
#     convert_wfm_to_npz(folder, show_plot=False)# make this true if you want to see plot of individual files.