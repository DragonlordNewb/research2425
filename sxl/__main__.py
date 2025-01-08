print("Loading SXL CLI ...")

from sxl.cli import SXL

sxl = SXL()

if __name__ == "__main__":
	sxl.loop()