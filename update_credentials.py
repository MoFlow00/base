import sys

USERNAME = sys.argv[1]
PASSWORD = sys.argv[2]

with open("base.m3u","r",encoding="utf-8") as f:
    data = f.read()

data = data.replace("{USERNAME}", USERNAME)
data = data.replace("{PASSWORD}", PASSWORD)

with open("final.m3u","w",encoding="utf-8") as f:
    f.write(data)

print("Generated")
