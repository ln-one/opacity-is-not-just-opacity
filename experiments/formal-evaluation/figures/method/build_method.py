"""Editable diagram comparing conventional contraction and extended expansion."""
from pathlib import Path
import base64,json,sys,xml.etree.ElementTree as E
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parents[1]))
from numerical import decode,encode,render
import numpy as np
PALETTE=['#EE7733','#0077BB','#EE3377']
BGS=['#FFFFFF','#181818']
source=decode(np.array([[int(h[k:k+2],16)/255 for k in (1,3,5)] for h in PALETTE]))
m=E.Element('mxfile',host='drawio',version='31.4.5');d=E.SubElement(m,'diagram',id='alpha-extension-effects',name='Contraction and expansion');g=E.SubElement(d,'mxGraphModel',grid='1',gridSize='10',page='0',background='none');root=E.SubElement(g,'root');E.SubElement(root,'mxCell',id='0');E.SubElement(root,'mxCell',id='1',parent='0')
def node(id,value,x,y,w,h,style):
 c=E.SubElement(root,'mxCell',id=id,value=value,style=style,vertex='1',parent='1');E.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
def text(id,value,x,y,w,h=28,size=18,color='#333333',bold=False):
 node(id,value,x,y,w,h,f'text;html=1;whiteSpace=wrap;align=center;verticalAlign=middle;strokeColor=none;fillColor=none;fontFamily=Arial;fontSize={size};fontColor={color};fontStyle={1 if bold else 0};')
def edge(id,x1,x2,y,color):
 c=E.SubElement(root,'mxCell',id=id,value='',style=f'edgeStyle=none;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor={color};strokeWidth=2.5;endArrow=classic;endFill=1;endSize=7;',edge='1',parent='1');q=E.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'});E.SubElement(q,'mxPoint',x=str(x1),y=str(y),attrib={'as':'sourcePoint'});E.SubElement(q,'mxPoint',x=str(x2),y=str(y),attrib={'as':'targetPoint'})
records=[]
def tile(alpha):
 s=['<svg xmlns="http://www.w3.org/2000/svg" width="120" height="150" viewBox="0 0 120 150">']
 for j,bg in enumerate(BGS):
  b=decode(np.array([int(bg[k:k+2],16)/255 for k in (1,3,5)]));out,_=render(source,b,str(alpha));q=np.rint(encode(out)*255).astype(np.uint8);colors=['#'+''.join(f'{v:02X}' for v in c) for c in q]
  if alpha==1:assert colors==PALETTE
  records.append({'alpha':alpha,'background':bg,'source':PALETTE,'output':colors})
  y=j*82;s.append(f'<rect x="0.5" y="{y+.5}" width="119" height="67" fill="{bg}" stroke="#BBBBBB" stroke-width="1"/>')
  s += [f'<circle cx="23" cy="{y+34}" r="11" fill="{colors[0]}"/>',f'<rect x="49" y="{y+23}" width="22" height="22" fill="{colors[1]}"/>',f'<path d="M 97 {y+21} L 110 {y+45} L 84 {y+45} Z" fill="{colors[2]}"/>']
 s.append('</svg>');return ''.join(s)
node('extension-frame','',525,34,450,350,'rounded=0;html=1;fillColor=none;strokeColor=#EE7733;strokeWidth=1.2;pointerEvents=0;')
for side,(x,title,alphas,technical,meaning,color) in enumerate([(40,'Conventional: 0 ≤ α ≤ 1',[0,.6,1],'Difference contraction','Blend into the background','#0077BB'),(540,'Extension: α > 1',[1,1.1,1.4],'Difference expansion','Stand out from the background','#EE7733')]):
 text(f'heading-{side}',title,x,48,420,size=22,bold=True)
 for j,a in enumerate(alphas):
  xx=x+j*150
  text(f'alpha-{side}-{j}',f'α = {a:.1f}',xx,95,120,size=18)
  svg=tile(a);(P/f'demo-{side}-{j}.svg').write_text(svg)
  uri='data:image/svg+xml,'+base64.b64encode(svg.encode()).decode()
  node(f'objects-{side}-{j}','',xx,138,120,150,f'shape=image;html=1;imageAspect=0;aspect=fixed;image={uri};')
  if j<2:
   start,end=(xx+145,xx+125) if side==0 else (xx+125,xx+145)
   edge(f'advance-{side}-{j}',start,end,111,color)
 text(f'technical-{side}',technical,x,309,420,size=21,color=color,bold=True)
 text(f'effect-{side}',meaning,x,342,420,size=19,color=color)
# Nest the extension content in its outline, preserving absolute positions.
for cell in root.findall('mxCell'):
 if cell.get('id','').startswith(('heading-1','alpha-1-','objects-1-','advance-1-','technical-1','effect-1')):
  cell.set('parent','extension-frame')
  geo=cell.find('mxGeometry')
  if cell.get('vertex')=='1':
   geo.set('x',str(float(geo.get('x'))-525))
   geo.set('y',str(float(geo.get('y'))-34))
  else:
   for point in geo.findall('mxPoint'):
    point.set('x',str(float(point.get('x'))-525))
    point.set('y',str(float(point.get('y'))-34))
E.indent(m);E.ElementTree(m).write(P/'method.drawio',encoding='utf-8',xml_declaration=True)
(P/'method-demo-data.json').write_text(json.dumps(records,indent=2)+'\n')
