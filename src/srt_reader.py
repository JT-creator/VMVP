import srt

File = 'examples/Tanzania-caption.srt'
with open(File, "r", encoding="utf-8") as f:
    subtitles = list(srt.parse(f.read()))

for sub in subtitles:
    print(sub.start, sub.end, sub.content)