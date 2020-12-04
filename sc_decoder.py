import os
import lzma
import struct
from PIL import Image
from utils.reader import Reader

def _(message):
    print("[INFO] " + message)


class ScDecode:
    def __init__(self, filename):
        self.filename = filename
        self.data = open(filename, 'rb').read()


    def convert_pixel(self, pixel, type):
        if type == 0:
            return struct.unpack('4B', pixel)
        elif type == 2:
            pixel, = struct.unpack('<H', pixel)
            return (((pixel >> 12) & 0xF) << 4, ((pixel >> 8) & 0xF) << 4,
                    ((pixel >> 4) & 0xF) << 4, ((pixel >> 0) & 0xF) << 4)
        elif type == 4:
            pixel, = struct.unpack("<H", pixel)
            return (((pixel >> 11) & 0x1F) << 3, ((pixel >> 5) & 0x3F) << 2, (pixel & 0x1F) << 3)
        elif type == 6:
            pixel, = struct.unpack("<H", pixel)
            return ((pixel >> 8), (pixel >> 8), (pixel >> 8), (pixel & 0xFF))
        elif type == 10:
            pixel, = struct.unpack("<B", pixel)
            return (pixel, pixel, pixel)
        else:
            raise Exception("Unknown pixel type: " + type)



    def decompile_sc(self):

        if self.data[0] != 93:
            self.data = self.data[26:]

        self.data = self.data[0:5] + b'\xff' * 8 + self.data[9:]
        decompressed = lzma.LZMADecompressor().decompress(self.data)


        self.r = Reader(decompressed)

        i = 0
        picCount = 0

        while len(decompressed[i:]) > 5:
            try:

                file_type = int.from_bytes(self.r.read(1), "little")
                file_size = self.r.read_uint32()
                sub_type = int.from_bytes(self.r.read(1), "little")
                width = self.r.read_uint16()
                height = self.r.read_uint16()

                if file_type == 0 and file_size == 0:
                    return

                _(f"File type: {file_type}, size: {file_size}, sub type: {sub_type}, width: {width}, height: {height} ")
                _("Creating picture...")

                i += 10

                if sub_type == 0:
                    pixel_size = 4
                else:
                    if sub_type == 2 or sub_type == 4 or sub_type == 6:
                        pixel_size = 2
                    elif sub_type == 10:
                        pixel_size = 1
                    else:
                        raise Exception("Unknown pixel type: " + sub_type)


                img = Image.new("RGBA", (width, height))

                pixels = []

                for y in range(height):
                    for x in range(width):
                        pixels.append(self.convert_pixel(self.r.read(pixel_size), sub_type))
                        i += pixel_size

                img.putdata(pixels)

                if file_type == 28 or file_type == 27:
                    imgl = img.load()
                    iSrcPix = 0
                    for l in range(int(height / 32)):
                        for k in range(int(width / 32)):
                            for j in range(32):
                                for h in range(32):
                                    imgl[h + (k * 32), j + (l * 32)] = pixels[iSrcPix]
                                    iSrcPix += 1
                        for j in range(32):
                            for h in range(width % 32):
                                imgl[h + (width - (width % 32)), j + (l * 32)] = pixels[iSrcPix]
                                iSrcPix += 1

                    for k in range(int(width / 32)):
                        for j in range(int(height % 32)):
                            for h in range(32):
                                imgl[h + (k * 32), j + (height - (height % 32))] = pixels[iSrcPix]
                                iSrcPix += 1

                    for j in range(height % 32):
                        for h in range(width % 32):
                            imgl[h + (width - (width % 32)), j + (height - (height % 32))] = pixels[iSrcPix]
                            iSrcPix += 1



                path, name = os.path.split(self.filename)
                a = name.split('\\')[-1].split('.')[0]
                fullname = a + ('_' * picCount)
                if not os.path.isdir(a):
                    os.mkdir(a)
                img.save(f"{a}/{fullname}.png", "PNG")
                picCount += 1
                _(f"Saved image to {a}/{a}.png ")

            except:
                pass


input_file = input("Enter the name of the _tex.sc (eg. loading_tex.sc)\n")


d = ScDecode(input_file)
d.decompile_sc()
