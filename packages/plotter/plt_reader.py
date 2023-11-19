from pathlib import Path

def parse_coords(str):
  if len(str) < 3:
    return []
  
  coords = str.split(",")
  if len(coords) % 2 != 0:
    print("INVALID COORDS")
    return []

  retval = []
  for i in range(len(coords) // 2):
    retval.append([int(coords[2*i]), int(coords[2*i+1])])
  return retval
  
def plt_commands(filename, max_height = 2000, max_width = 2000, border = 200, multiplier = 1.0):
  cmds = []
  data = []
  xvals = []
  yvals = []

  text = Path(filename).read_text().replace('\n', '')
  commands = text.split(";")

  for row in commands:
    coords = parse_coords(row[2:])
    for [x,y] in coords:
      xvals.append(x)
      yvals.append(y)

  minx = min(xvals)
  miny = min(yvals)
  maxx = max(xvals)
  maxy = max(yvals)
  oldsize = [maxx-minx, maxy-miny]

  scale = min([multiplier, max_width / oldsize[0], max_height / oldsize[1]])
  newsize = [i*scale for i in oldsize]
  print("Old size: %s, Scale factor: %f, New size: %s" % (oldsize, scale, newsize))

  def transform(coord):
      x=(coord[0]-minx) * scale - border - max_width
      y=(coord[1]-miny) * scale + border
      return [x, y]
    
  
  for row in commands:
    if len(row) < 2:
      continue

    cmd = row[0:2]
    coords = parse_coords(row[2:])
    
    if cmd == "IN":
      cmds.append(["PI", lambda p: p.init()])
    elif cmd == "PU":
      cmds.append(["PU", lambda p: p.pen(True)])
      for coord in coords:
        [x, y] = transform(coord)
        cmds.append(["PU (%d, %d)" % (x, y), lambda p, x=x, y=y: p.go(round(x), round(y))])
    elif cmd == "PD":
      cmds.append(["PD", lambda p: p.pen(False)])
      for coord in coords:
        [x, y] = transform(coord)
        cmds.append(["PD (%d, %d)" % (x, y), lambda p, x=x, y=y: p.go(round(x), round(y))])
    elif cmd == "SP":
      # select pen
      pass
    elif cmd == "PR":
      print("RELATIVE MOVEMENT NOT SUPPORTED")
    elif cmd == "PA":
      for coord in coords:
        [x, y] = transform(coord)
        cmds.append(["PA (%d, %d)" % (x, y), lambda p, x=x, y=y: p.go(round(x), round(y))])
    else:
      print("Unknown cmd: '%s'" % cmd)
      exit(1)
  return cmds

    
if __name__ == '__main__':
  import os
  datadir = os.path.dirname(__file__) + "/data/"
  for file in os.listdir(datadir):
    if file.endswith(".plt") or file.endswith("hpgl"):
      print(file)
      cmds = plt_commands(datadir + file)
      #for cmd in cmds:
      #  print(cmd[0])
