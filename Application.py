import tkinter as tk
import os
import subprocess
import json
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk
import heapq
import struct

# Node class for text document compression
class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq
         
# Create the foundation for window
root = tk.Tk()
root.title("Data Compression Program")
root.geometry("800x500")
style = ttk.Style()
style.theme_use('default')
# Fonts and Styles
large_font = ("TkDefaultFont", 16, "bold")
regular_font = ("TkDefaultFont", 12)
small_font = ("TkDefaultFont", 9)

# File Selection Style
style.configure("Top.TButton", 
                font=("Helvetica", 12), 
                padding=10, 
                relief="flat", 
                background="lightgray",
                foreground="black",
                borderwidth=1, 
                focuscolor="none")

style.configure("Top.TButton.active", 
                background="blue",
                foreground="white")

style.configure("Compress.TButton", 
                font=("Helvetica", 12), 
                padding=10, 
                relief="flat", 
                background="lightblue",
                foreground="black",
                borderwidth=1, 
                focuscolor="none")

# Active button
active_button = None
# File Selected variable
selected = tk.BooleanVar(value=False)
# File type variable
selected_file_type = tk.StringVar(value="None")
selected_file_ext = tk.StringVar(value="None")
alg_selected = tk.StringVar(value="None")
# Input file properties
input_duration = tk.StringVar(value="None")
input_width = tk.IntVar(value=0)
input_height = tk.IntVar(value=0)
input_bitrate = tk.IntVar(value=0)
input_framerate = tk.IntVar(value=0)
input_bitdepth = tk.StringVar(value="None")
input_dpi = tk.IntVar(value=0)
# File extensions
text_ext = {"docx", "txt", "text", "pdf", "doc", "log", "html"}
image_ext = {"jpg", "jpeg", "png", "tiff", "bmp", "webp", "gif"}
video_ext = {"mp4", "mov", "avi", "wmv", "webm", "flv", "mkv"}
# File extension buttons
file_type_buttons = {
    "text": ["Huffman", "Lempel-Ziv"],
    "image": ["JPEG", "PNG", "WebP"],
    "video": ["H.264", "H.265", "VP9"],
}

# Function to determine file type based on extension
def get_file_type(file_path):
    _, ext = os.path.splitext(file_path)
    ext = ext.lower().strip(".")
    print(f"File extension detected: {ext}")
    selected_file_ext.set(ext)
    if ext in text_ext:
        print("File type: text")
        return "text"
    elif ext in image_ext:
        print("File type: image")
        return "image"
    elif ext in video_ext:
        print("File type: video")
        return "video"
    elif ext == "huff":
        print("File type: huffman compressed")
        return "compressed_huff"
    elif ext == "lz77":
        print("File type: lempel-ziv compressed")
        return "compressed_lz77"
    else:
        print("File type unsupported")
        return "unsupported"

# Function to update buttons for compression and decompression of different algorithms
def update_status_label(*args):
    if selected.get():
        file_type = selected_file_type.get()
        status_label.config(text="File Loaded")
        if file_type == "compressed_huff" or file_type == "compressed_lz77":
            """ Decompression buttons and hide algorithm buttons """
            compress_button.config(text="Decompress")
            for widget in button_frame.winfo_children():
                widget.destroy()
            for widget in middle_section_1.winfo_children():
                    widget.destroy()
            for widget in middle_section_2.winfo_children():
                    widget.destroy()
            for widget in middle_section_3.winfo_children():
                    widget.destroy()
            button_frame.pack_forget()
        else:
            """ Compression buttons """
            compress_button.config(text="Compress")
            buttons = file_type_buttons.get(file_type, [])
            for widget in button_frame.winfo_children():
                widget.destroy()
            if buttons:
                for button_text in buttons:
                    button = ttk.Button(button_frame, text=button_text, style="Top.TButton")
                    button.config(command=lambda bt=button_text, btn=button: algorithm_click(bt, btn))
                    button.pack(side="left", padx=5)
                button_frame.pack(expand=False)
            else:
                status_label.config(text="Unsupported file type")
                button_frame.pack_forget()
    else:
        status_label.config(text="Waiting for File Input")
        for widget in button_frame.winfo_children():
            widget.destroy()
        button_frame.pack_forget()

# Function to open the file
def open_file():
    global file_path
    file_path = filedialog.askopenfilename(title="Select a File")
    if file_path:
        file_path_entry.delete(0, tk.END)
        file_path_entry.insert(0, file_path)
        selected.set(True)
        file_type = get_file_type(file_path)
        selected_file_type.set(file_type)
        update_status_label()
        file_properties(middle_section_1, file_path)
    
# Function to display the file properties, input and output
def file_properties(section, file):
    """ Deletes any current properties displayed """
    for widget in section.winfo_children():
        widget.destroy()
    
    if section == middle_section_1:
        properties_title = "Input"
    if section == middle_section_3:
        properties_title = "Output"

    if selected_file_type.get() == "video":
        """ Get the video file properties """
        duration, width, height, bit_rate, frame_rate = get_video_properties(file)
        file_size = os.path.getsize(file) / (1024 * 1024)
        """ If properties are found """
        if width and height:
            tk.Label(section, text=f"{properties_title} properties:", font=large_font).pack(expand=False)
            tk.Label(section, text=f"File size: {file_size:.2f} MB", font=regular_font).pack(expand=False)
            tk.Label(section, text=f"Duration: {format_duration(float(duration))}", font=regular_font).pack(expand=False)
            tk.Label(section, text=f"Width: {width}px", font=regular_font).pack(expand=False)
            tk.Label(section, text=f"Height: {height}px", font=regular_font).pack(expand=False)
            tk.Label(section, text=f"Bit rate: {bit_rate:.0f}", font=regular_font).pack(expand=False)
            tk.Label(section, text=f"Frame rate: {frame_rate:.0f} FPS", font=regular_font).pack(expand=False)
            """ Noting down the properties for calculating the changes after compression """
            if section == middle_section_1:
                global input_size
                input_size = file_size
                input_duration.set(duration)
                input_width.set(width)
                input_height.set(height)
                input_bitrate.set(bit_rate)
                input_framerate.set(frame_rate)
            """ Calculating the compression changes """
            if section == middle_section_3:
                """ Deletes any current displays in the changes box """
                for widget in middle_section_2.winfo_children():
                    widget.destroy()
                """ Calculations """
                file_size_diff = file_size - input_size
                duration_diff = float(duration) - float(input_duration.get())
                width_diff = width - input_width.get()
                height_diff = height - input_height.get()
                bit_rate_diff = bit_rate - input_bitrate.get()
                frame_rate_diff = frame_rate - input_framerate.get()
                file_size_perc = (1 - (file_size / input_size)) * 100
                """ Displaying calculated changes """
                tk.Label(middle_section_2, text="Video changes:", font=large_font).pack(expand=False)
                tk.Label(middle_section_2, text=f"File size: {file_size_diff:.2f} MB ({file_size_perc:.2f}%)" if file_size_diff != 0 else "File size: No change", font=regular_font).pack(expand=False)
                tk.Label(middle_section_2, text=f"Duration: {duration_diff}" if duration_diff != 0 else "Duration: No change", font=regular_font).pack(expand=False)
                tk.Label(middle_section_2, text=f"Width: {width_diff}px" if width_diff != 0 else "Width: No change", font=regular_font).pack(expand=False)
                tk.Label(middle_section_2, text=f"Height: {height_diff}px" if height_diff != 0 else "Height: No change", font=regular_font).pack(expand=False)
                tk.Label(middle_section_2, text=f"Bit rate: {bit_rate_diff:.0f}" if bit_rate_diff != 0 else "Bit rate: No change", font=regular_font).pack(expand=False)
                tk.Label(middle_section_2, text=f"Frame rate: {frame_rate_diff:.0f} FPS" if frame_rate_diff != 0 else "Frame rate: No change", font=regular_font).pack(expand=False)
    elif selected_file_type.get() == "image":
        print("image")
        try:
            with Image.open(file) as img:
                width, height = img.size
                bit_depth = img.mode
                dpi = img.info.get('dpi')
                print(dpi)
                file_size = os.path.getsize(file) / (1024 * 1024)
                tk.Label(section, text=f"{properties_title}", font=large_font).pack(expand=False)
                tk.Label(section, text=f"File size: {file_size:.2f} MB", font=regular_font).pack(expand=False)
                tk.Label(section, text=f"Width: {width}px", font=regular_font).pack(expand=False)
                tk.Label(section, text=f"Height: {height}px", font=regular_font).pack(expand=False)
                tk.Label(section, text=f"Bit depth: {bit_depth}", font=regular_font).pack(expand=False)
                tk.Label(section, text=f"DPI: {dpi}", font=regular_font).pack(expand=False)
                if section == middle_section_1:
                    input_size = file_size
                    input_width.set(width)
                    input_height.set(height)
                    input_bitdepth.set(bit_depth)
                """ Calculating the compression changes """
                if section == middle_section_3:
                    """ Deletes any current displays in the changes box """
                    for widget in middle_section_2.winfo_children():
                        widget.destroy()
                    """ Calculations """
                    file_size_diff = file_size - input_size
                    width_diff = width - input_width.get()
                    height_diff = height - input_height.get()
                    file_size_perc = (1 - (file_size / input_size)) * 100
                    """ Displaying calculated changes """
                    tk.Label(middle_section_2, text="Image changes:", font=large_font).pack(expand=False)
                    tk.Label(middle_section_2, text=f"File size: {file_size_diff:.2f} MB ({file_size_perc:.2f}%)" if file_size_diff != 0 else "File size: No change", font=regular_font).pack(expand=False)
                    tk.Label(middle_section_2, text=f"Width: {width_diff}px" if width_diff != 0 else "Width: No change", font=regular_font).pack(expand=False)
                    tk.Label(middle_section_2, text=f"Height: {height_diff}px" if height_diff != 0 else "Height: No change", font=regular_font).pack(expand=False)
                    tk.Label(middle_section_2, text=f"Bit depth: {bit_depth}" if bit_depth != input_bitdepth.get() else "Bit depth: No change", font=regular_font).pack(expand=False)
        except Exception as e:
            tk.Label(section, text=f"Error loading image: {str(e)}", font=regular_font).pack(expand=True)
    elif selected_file_type.get() == "text":
        print("text")
        file_size = os.path.getsize(file) / (1024 * 1024)
        tk.Label(section, text=f"{properties_title} properties:", font=large_font).pack(expand=False)
        tk.Label(section, text=f"File size: {file_size:.2f} MB", font=regular_font).pack(expand=False)
        if section == middle_section_1:
            input_size = file_size
        if section == middle_section_3:
            for widget in middle_section_2.winfo_children():
                widget.destroy()
            file_size_diff = file_size - input_size
            file_size_perc = (1 - (file_size / input_size)) * 100 if input_size != 0 else 0
            tk.Label(middle_section_2, text="Text changes:", font=large_font).pack(expand=False)
            tk.Label(middle_section_2, text=f"File size: {file_size_diff:.2f} MB ({file_size_perc:.2f}%)" if file_size_diff != 0 else "File size: No change", font=regular_font).pack(expand=False)

# Function to get video file properties
def get_video_properties(file_path):
    command = [
        "ffprobe", 
        "-v", "quiet", 
        "-print_format", "json", 
        "-show_streams", 
        file_path
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        data = json.loads(result.stdout)
        for stream in data["streams"]:
            if stream["codec_type"] == "video":
                duration = stream["duration"]
                width = stream["width"]
                height = stream["height"]
                bit_rate = stream["bit_rate"]
                frame_rate = stream["r_frame_rate"]
                """ Convert to kbps """
                if bit_rate:
                    bit_rate_kbps = int(bit_rate) / 1000
                """ Convert to readible FPS Value """
                # Calculate FPS from r_frame_rate
                if frame_rate:
                    num, denom = frame_rate.split('/')
                    frame_rate = float(num) / float(denom)

                return duration, width, height, bit_rate_kbps, frame_rate
    return None, None
    
# Function to format video file durations correctly
def format_duration(duration):
    """ Convert secconds to hours/minutes """
    hours = int(duration // 3600)
    minutes = int((duration % 3600) // 60)
    seconds = int(duration % 60)
    formatted_duration = f"{hours:02}:{minutes:02}:{seconds:02}"
    return formatted_duration

# Function to close file
def close_file():
    file_path_entry.delete(0, tk.END)
    selected.set(False)
    for widget in middle_section_1.winfo_children():
        widget.destroy()
    for widget in middle_section_2.winfo_children():
        widget.destroy()
    for widget in middle_section_3.winfo_children():
        widget.destroy()
    global active_button
    active_button = None

# Function for selecting algorithm
def algorithm_click(button_text, button):
    global active_button
    
    """ Reset the previous active button (if any) """
    if active_button:
        active_button.state(["!pressed"])
    
    """ Set the new active button and algorithm """
    button.state(["pressed"])
    active_button = button
    
    alg_selected.set(button_text) 
    print(f"Selected algorithm: {alg_selected.get()}") 

# Function for the compression process
def process_file():
    if selected_file_type.get() == "compressed_huff":
        decompress_huffman(file_path)
    if selected_file_type.get() == "compressed_lz77":
        decompress_lz77(file_path)
    else:
        if alg_selected.get() == "H.264":
            output_file = os.path.splitext(file_path)[0] + "_compressed.mp4"
            command = [
                "ffmpeg",
                "-i", file_path,  
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                output_file        
            ]
            subprocess.run(command)
        
        if alg_selected.get() == "H.265":
            output_file = os.path.splitext(file_path)[0] + "_compressed.mp4"
            command = [
                "ffmpeg",
                "-i", file_path,  
                "-c:v", "libx265",
                "-preset", "fast",
                "-crf", "23",      
                output_file        
            ]
            subprocess.run(command)
        
        if alg_selected.get() == "VP9":
            output_file = os.path.splitext(file_path)[0] + "_compressed.mp4"
            command = [
                "ffmpeg",
                "-i", file_path,  
                "-c:v", "libvpx-vp9", 
                "-b:v", "10M",
                "-preset", "fast", 
                "-crf", "23",      
                output_file        
            ]
            subprocess.run(command)

        if alg_selected.get() == "JPEG":
            output_file = os.path.splitext(file_path)[0] + "_compressed.jpg"
            image = Image.open(file_path)
            image.save(output_file, "JPEG", quality=75)
        
        if alg_selected.get() == "PNG":
            output_file = os.path.splitext(file_path)[0] + "_compressed.png"
            image = Image.open(file_path)
            image.save(output_file, "PNG", compress_level=6)

        if alg_selected.get() == "WebP":
            output_file = os.path.splitext(file_path)[0] + "_compressed.webp"
            image = Image.open(file_path)
            image.save(output_file, "WebP", losless=True)

        if alg_selected.get() == "Huffman":
            _, ext = os.path.splitext(file_path)
            ext = ext.lower().strip(".")
            """ Read the bytes of the document """
            with open(file_path, 'rb') as file:
                data = file.read()
            
            """ Build a frequency table for the bytes """
            frequency = {}
            for byte in data:
                frequency[byte] = frequency.get(byte, 0) + 1
            
            """ Build the huffman tree """
            nodes = []
            for byte, freq in frequency.items():
                heapq.heappush(nodes, Node(byte, freq))
            
            """ Handle no bytes/empty file and single bytes"""
            if len(nodes) == 0:
                return
            elif len(nodes) == 1:
                node = nodes[0]
                codes = {node.char: "0"}
            else:
                while len(nodes) > 1:
                    left = heapq.heappop(nodes)
                    right = heapq.heappop(nodes)
                    merged = Node(None, left.freq + right.freq)
                    merged.left = left
                    merged.right = right
                    heapq.heappush(nodes, merged)
                
                """ Generate huffman codes """
                codes = {}
                def build_codes(node, current_code):
                    if node.char is not None:
                        codes[node.char] = current_code or "0" 
                        return
                    build_codes(node.left, current_code + "0")
                    build_codes(node.right, current_code + "1")
                build_codes(nodes[0], "")
                
            """ Encode the codes/tree into a single file """
            encoded_text = "".join(codes[byte] for byte in data)
            output_file = os.path.splitext(file_path)[0] + "_compressed." + ext + ".huff"
            with open(output_file, 'wb') as file:
                """ Identify number of bytes """
                N = len(frequency)
                file.write(N.to_bytes(4, 'big'))
                """ Write the frequency table in """
                for byte, freq in frequency.items():
                    file.write(byte.to_bytes(1, 'big'))
                    file.write(freq.to_bytes(4, 'big'))
                total_bits = len(encoded_text)
                file.write(total_bits.to_bytes(4, 'big'))
                """ Write the encoded codes into a byte array """
                byte_array = bytearray()
                for i in range(0, len(encoded_text), 8):
                    byte_str = encoded_text[i:i+8]
                    if len(byte_str) < 8:
                        byte_str = byte_str.ljust(8, '0') 
                    byte_array.append(int(byte_str, 2))
                file.write(byte_array)
            
            """ Indicate compression end """
            compress_button.config(text="Done...")
            file_properties(middle_section_3, output_file)
            compress_section.after(3000, lambda: compress_button.config(text="Compress"))
        
        elif alg_selected.get() == "Lempel-Ziv":
            _, ext = os.path.splitext(file_path)
            ext = ext.lower().strip(".")
            """ Read the bytes of the document """
            with open(file_path, 'rb') as f:
                data = f.read()

            i = 0
            compressed = []
            window_size = 4096
            lookahead_size = 18

            while i < len(data):
                match_heap = []
                end_of_buffer = min(i + lookahead_size, len(data))

                """ Find the longest matching patterns """
                for j in range(max(0, i - window_size), i):
                    length = 0
                    while length < lookahead_size and i + length < len(data) and data[j + length] == data[i + length]:
                        length += 1

                    if length > 0:
                        heapq.heappush(match_heap, (-length, j))

                if match_heap:
                    best_match = heapq.heappop(match_heap)
                    length = -best_match[0]
                    offset = i - best_match[1]
                    next_char = data[i + length] if i + length < len(data) else None
                else:
                    length = 0
                    offset = 0
                    next_char = data[i]

                compressed.append((offset, length, next_char))
                i += length + 1

            """ Encode and combine into single output file """
            output_file = os.path.splitext(file_path)[0] + "_compressed." + ext + ".lz77"
            with open(output_file, 'wb') as f:
                for offset, length, next_char in compressed:
                    f.write(struct.pack('>HBB', offset, length, next_char if next_char is not None else 0))
        """ Indicate compression end """
        compress_button.config(text="Done...")
        file_properties(middle_section_3, output_file)
        compress_section.after(3000, lambda: compress_button.config(text="Compress"))

# Function to decompress lempel-ziv compressed documents
def decompress_lz77(file_path):
    """ Read the byte data of the file """
    with open(file_path, 'rb') as f:
        compressed = []
        while chunk := f.read(4):
            if len(chunk) < 4:
                if len(chunk) > 0:
                    print("Warning: Compressed file has incomplete chunk")
                break
            offset, length, next_char = struct.unpack('>HBB', chunk)
            compressed.append((offset, length, next_char))

    decompressed_data = bytearray()

    """ Decompress the file """
    for offset, length, next_char in compressed:
        if length > 0:
            start = len(decompressed_data) - offset
            if start < 0:
                raise ValueError("Invalid offset in compressed data")
            for _ in range(length):
                decompressed_data.append(decompressed_data[start])
                start += 1
        decompressed_data.append(next_char)

    """ Extract the original file extension """
    base_name = os.path.basename(file_path)
    if "_compressed." in base_name:
        original_extension = base_name.split("_compressed.", 1)[-1].rsplit(".lz77", 1)[0]
    else:
        original_extension = "txt"

    """ Combine and save to a single output file """
    output_file = os.path.splitext(file_path)[0].rsplit("_compressed", 1)[0] + "_decompressed." + original_extension
    with open(output_file, 'wb') as f:
        f.write(decompressed_data)

    """ Indicate decompression end """
    file_properties(middle_section_3, output_file)
    compress_button.config(text="Done...")
    compress_section.after(3000, lambda: compress_button.config(text="Decompress" if selected_file_type.get() == "compressed" else "Compress"))

# Function to decompress huffman compressed documents
def decompress_huffman(file_path):
    """ Read the bytes of the document """
    with open(file_path, 'rb') as file:
        N = int.from_bytes(file.read(4), 'big')
        frequency = {}
        for _ in range(N):
            byte = file.read(1)[0]
            freq = int.from_bytes(file.read(4), 'big')
            frequency[byte] = freq
        total_bits = int.from_bytes(file.read(4), 'big')
        encoded_data = file.read()

    """ Convert data to a bit string """
    bit_string = ''.join(f'{byte:08b}' for byte in encoded_data)[:total_bits]

    """ Rebuild the huffman tree """
    nodes = []
    for byte, freq in frequency.items():
        heapq.heappush(nodes, Node(byte, freq))
    if not nodes:
        decoded_data = []
    elif len(nodes) == 1:
        root = nodes[0]
    else:
        while len(nodes) > 1:
            left = heapq.heappop(nodes)
            right = heapq.heappop(nodes)
            merged = Node(None, left.freq + right.freq)
            merged.left = left
            merged.right = right
            heapq.heappush(nodes, merged)
        root = nodes[0]

    """ Decode the string data """
    decoded_data = []
    current_node = root
    for bit in bit_string:
        if bit == '0':
            current_node = current_node.left
        else:
            current_node = current_node.right
        if current_node.char is not None:
            decoded_data.append(current_node.char)
            current_node = root

    """ Extract the original file extension """
    base_name = os.path.basename(file_path)
    if "_compressed." in base_name:
        original_extension = base_name.split("_compressed.", 1)[-1].rsplit(".huff", 1)[0]
    else:
        original_extension = "txt"

    """ Encode and combine into a single output file """
    output_file = os.path.splitext(file_path)[0].rsplit("_compressed", 1)[0] + "_decompressed." + original_extension
    with open(output_file, 'wb') as file:
        file.write(bytes(decoded_data))

    """ Indicate decompression end """
    file_properties(middle_section_3, output_file)
    compress_button.config(text="Done...")
    compress_section.after(3000, lambda: compress_button.config(text="Decompress" if selected_file_type.get() == "compressed" else "Compress"))

# Create grid to maintain a layout shape
""" Columns """
root.columnconfigure(0, weight=4) # top
root.columnconfigure(1, weight=1) # mid
root.columnconfigure(2, weight=4) # bot
""" Rows """
root.rowconfigure(0, weight=5)  # top
root.rowconfigure(1, weight=10)  # mid
root.rowconfigure(2, weight=5)  # bot
root.rowconfigure(3, weight=1)  # button

# Creates top section (Selecting file)
top_section = tk.Frame(root)
top_section.grid(row=0, column=0, columnspan=3, sticky="nsew")
top_section.grid_propagate(False)
""" Sets a default label """
tk.Label(top_section, text="Select File", font=large_font).pack(expand=False)
""" Extra frame for a border """
border_frame = tk.Frame(top_section, bg="black", padx=2, pady=2)
border_frame.pack(expand=False)
""" Frame for browse and clear buttons """
file_input_frame = tk.Frame(border_frame, bg="lightgrey")
file_input_frame.pack(expand=False)
""" Entry box to display file path """
file_path_entry = ttk.Entry(file_input_frame, width=40, style="Top.TButton")
file_path_entry.pack(side="left")
""" Browse selection button """
browse_button = ttk.Button(file_input_frame, text="Browse", style="Top.TButton", command=open_file)
browse_button.pack(side="left", padx=0, pady=0)
""" Clear selection button """
clear_button = ttk.Button(file_input_frame, text="Clear", style="Top.TButton", command=close_file)
clear_button.pack(side="left", padx=0, pady=0)

# Creates middle section (input, changes, output)
middle_section_1 = tk.Frame(root)
middle_section_2 = tk.Frame(root)
middle_section_3 = tk.Frame(root)
""" Sets section positions """
middle_section_1.grid(row=1, column=0, sticky="nsew")
middle_section_2.grid(row=1, column=1, sticky="nsew")
middle_section_3.grid(row=1, column=2, sticky="nsew")

# Creates bottom section (Selecting algorithm)
bottom_section = tk.Frame(root)
bottom_section.grid(row=2, column=0, columnspan=3, sticky="nsew")
bottom_section.grid_propagate(False)
""" Sets a default label """
tk.Label(bottom_section, text="Select Data Compression Algorithm", font=large_font).pack(expand=False)
status_label = tk.Label(bottom_section, text="Waiting for File Input", font=regular_font)
status_label.pack(expand=False)
""" Creates frame for the algorithm buttons """
button_frame = tk.Frame(bottom_section)
button_frame.pack(expand=False)

# Compress button section
compress_section = tk.Frame(root)
compress_section.grid(row=3, column=0, columnspan=3, sticky="nsew")
compress_section.grid_propagate(False)
""" Extra frame for a border """
compress_frame = tk.Frame(compress_section, bg="black", padx=2, pady=2)
compress_frame.pack(expand=False)
""" Compress button """
compress_button = ttk.Button(compress_frame, text="Compress", style="Compress.TButton", command=process_file)
compress_button.pack(side="top", padx=0, pady=0)

# Attach the update function to the BooleanVar
selected.trace_add("write", update_status_label)

# Run the Tkinter event loop
root.mainloop()
