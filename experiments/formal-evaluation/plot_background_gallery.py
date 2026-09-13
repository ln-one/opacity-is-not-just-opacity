"""Full-corpus near-source illustrative plates; no outcome-based icon selection."""
from pathlib import Path
import io,json,hashlib,subprocess,sys,xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from figure_checks import require_matplotlib_panel_alignment
P=Path(__file__).resolve().parent; OUT=P/'figures'; OUT.mkdir(exist_ok=True)
PALETTE=['#EE7733','#0077BB','#33BBEE','#EE3377','#CC3311','#009988','#BBBBBB']
ORDER=[('Red',4),('Orange',0),('Teal',5),('Cyan',2),('Blue',1),('Magenta',3),('Grey',6),('Dark grey',None)]
MIX=.10; ALPHAS=[1.,2.]; COLS=25; ROWS=12; PITCH=96; SIZE=72; PAD=12
plt.rcParams.update({'font.family':'Arial','font.size':8,'pdf.fonttype':42,'svg.fonttype':'none'})
manifest=json.loads((P/'assets/manifest.json').read_text());assert len(manifest['icons'])==300
ns='http://www.w3.org/2000/svg'; ET.register_namespace('',ns)
svg=ET.Element('{'+ns+'}svg',{'width':str(COLS*PITCH),'height':str(ROWS*PITCH),'viewBox':f'0 0 {COLS*PITCH} {ROWS*PITCH}'})
for i,entry in enumerate(manifest['icons']):
 data=(P/'assets'/entry['name']).read_bytes();assert hashlib.sha256(data).hexdigest()==entry['sha256']
 node=ET.fromstring(data.replace(b'currentColor',b'#ffffff'));node.set('x',str((i%COLS)*PITCH+PAD));node.set('y',str((i//COLS)*PITCH+PAD));node.set('width',str(SIZE));node.set('height',str(SIZE));svg.append(node)
mask_png=subprocess.check_output(['rsvg-convert','--format=png'],input=ET.tostring(svg))
q=np.asarray(Image.open(io.BytesIO(mask_png)).convert('RGBA'))[:,:,3].astype(np.float32)/255
src=np.array([[int(h[k:k+2],16)/255 for k in (1,3,5)]for h in PALETTE])
def lin(x):return np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4)
def enc(x):return np.where(x<=.0031308,12.92*x,1.055*x**(1/2.4)-.055)
indices=(np.arange(q.shape[0])[:,None]//PITCH*COLS+np.arange(q.shape[1])[None,:]//PITCH)%7
source=lin(src)[indices]; entries=[]
for name,i in ORDER:
 bg=np.full(3,36/255) if i is None else np.round(255*((1-MIX)*src[i]+MIX))/255
 if i is not None: assert not np.array_equal(bg,src[i])
 b=lin(bg)
 for a in ALPHAS:
  obj=np.clip(b+a*(source-b),0,1);rgb=q[:,:,None]*obj+(1-q[:,:,None])*b
  result=np.round(255*np.clip(enc(rgb),0,1)).astype(np.uint8)
  path=OUT/f'gallery-{name.lower()}-{a:.1f}.png';Image.fromarray(result).save(path)
  entries.append({'background':name,'source_index':i,'background_hex':'#'+''.join(f'{round(c*255):02X}'for c in bg),'alpha':a,'file':path.name})
# All panels share physical dimensions and equal gutters; 25x12 reflow retains every icon.
width=178.;gutter=6.;pw=(width-gutter)/2;ph=pw*ROWS/COLS;stride=ph+5
for page,names in enumerate([ORDER[:4],ORDER[4:]],1):
 height=len(names)*stride+7;fig=plt.figure(figsize=(width/25.4,height/25.4));axes=[]
 fig.text(pw/2/width,1-2/height,r'Original · $\alpha=1.0$',ha='center',va='top',fontsize=9)
 fig.text((pw+gutter+pw/2)/width,1-2/height,r'$\alpha=2.0$',ha='center',va='top',fontsize=9)
 for row,(name,index) in enumerate(names):
  top=height-10-row*stride
  fig.text(0,(top+2)/height,name,ha='left',va='bottom',fontsize=8,fontweight='bold')
  for col,a in enumerate(ALPHAS):
   ax=fig.add_axes([col*(pw+gutter)/width,(top-ph)/height,pw/width,ph/height]);axes.append(ax)
   ax.imshow(Image.open(OUT/f'gallery-{name.lower()}-{a:.1f}.png'),interpolation='none');ax.set_axis_off()
 fig.canvas.draw();base=OUT/f'background-gallery-{page}'
 require_matplotlib_panel_alignment(fig,json_out=str(base)+'.alignment.json',strict=True, row_groups=[[chr(97+2*r),chr(98+2*r)]for r in range(len(names))],column_groups=[[chr(97+2*r+c)for r in range(len(names))]for c in range(2)])
 fig.savefig(str(base)+'.pdf');fig.savefig(str(base)+'.svg');fig.savefig(str(base)+'.png',dpi=300);plt.close(fig)
protocol={'purpose':'Selected near-source visual comparisons, not recognition or aggregate-performance evidence.','backend':'Python; librsvg decodes SVG coverage masks, NumPy performs linear-light compositing, Matplotlib assembles plates. Not WebGL screenshots.','icons':300,'icon_manifest_sha256':hashlib.sha256((P/'assets/manifest.json').read_bytes()).hexdigest(),'order':'Red, Orange, Teal, Cyan, Blue, Magenta, Grey, Dark grey; warm through cool hues, neutrals last.','columns':COLS,'rows':ROWS,'icon_raster_px':SIZE,'pitch_px':PITCH,'panel_width_mm':pw,'panel_height_mm':ph,'effective_dpi':COLS*PITCH/(pw/25.4),'white_mix_encoded_srgb':MIX,'alphas':ALPHAS,'edge_coverage':'Linear-light interpolation after clipping; identical to the paper formula.','cases':entries}
(OUT/'background-gallery-protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
print('Generated 16 arrays and two aligned plates.',pw,ph,'mm')
