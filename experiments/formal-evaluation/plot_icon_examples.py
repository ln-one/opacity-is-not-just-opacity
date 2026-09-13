"""Assemble unretouched, captured WebGL icon pixels into a matched image plate."""
from pathlib import Path
import sys,json,base64
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'vendor-python'))
sys.path.insert(0,str(Path.home()/'.codex/skills/nature-figure/scripts'))
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from audit_panel_alignment import require_matplotlib_panel_alignment
from numerical import decode,encode,render
O=P/'figures'
D=json.loads((O/'icon-examples-source.json').read_text())
SIZE=D['size'];SCALE=SIZE//24;ALPHAS=[.6,1,1.4];BGS=['#FFFFFF','#181818']
def rgb(h):return np.array([int(h[k:k+2],16)/255 for k in (1,3,5)])
def pixels(s):return np.frombuffer(base64.b64decode(s),dtype=np.uint8).reshape(SIZE,SIZE,4)
def plates():
 images={};maxerr=0
 for bg in BGS:
  bg8=np.rint(rgb(bg)*255).astype(np.uint8);b=decode(rgb(bg))
  img=np.broadcast_to(bg8,(156*SCALE,280*SCALE,3)).copy()
  for j,a in enumerate(ALPHAS):
   case=next(c for c in D['cases'] if c['background']==bg and c['alpha']==a)
   for i,(icon,raw) in enumerate(zip(D['icons'],case['rgba'])):
    q=pixels(raw);mask=pixels(icon['sourceRgba'])[...,3:4]/255.
    out,_=render(decode(rgb(icon['source'])),b,str(a))
    ref=np.rint(255*encode(mask*out+(1-mask)*b)).astype(np.int16)
    err=int(np.max(np.abs(q[...,:3].astype(np.int16)-ref)));maxerr=max(maxerr,err)
    assert err<=1,(icon['name'],bg,a,err)
    assert np.all(q[...,3]==255)
    img[(j*52+14)*SCALE:(j*52+14)*SCALE+SIZE,(i*40+8)*SCALE:(i*40+8)*SCALE+SIZE]=q[...,:3]
  images[bg]=img
 (O/'icon-examples-verification.json').write_text(json.dumps({'maxByteError':maxerr,'instances':42,'rgbChannelsChecked':42*SIZE*SIZE*3,'toleranceBytes':1},indent=2)+'\n')
 return images

def draw(theme,images):
 dark=theme=='dark';face='#181A1B' if dark else '#FFFFFF';fg='#E8E6E3' if dark else '#222222'
 mpl.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','DejaVu Sans'],'font.size':8,'svg.fonttype':'none','pdf.fonttype':42,'figure.facecolor':face,'text.color':fg,'savefig.facecolor':face})
 fig,axs=plt.subplots(2,1,figsize=(89/25.4,112/25.4),gridspec_kw={'hspace':.32})
 fig.subplots_adjust(left=.19,right=.98,bottom=.035,top=.91)
 for k,(ax,bg) in enumerate(zip(axs,BGS)):
  ax.imshow(images[bg],interpolation='antialiased',extent=(0,280,156,0),aspect='equal')
  ax.set_xticks([]);ax.set_yticks([])
  for sp in ax.spines.values():sp.set_visible(False)
  ax.annotate('ab'[k],(0,1),xycoords='axes fraction',xytext=(0,10),textcoords='offset points',weight='bold',fontsize=9,ha='left',va='bottom')
  ax.set_title('Light canvas' if k==0 else 'Dark canvas',loc='left',x=.08,pad=10,fontsize=9)
  for j,a in enumerate(ALPHAS):
   ax.annotate(f'α = {a:.1f}',(0,j*52+26),xycoords='data',xytext=(-8,0),textcoords='offset points',ha='right',va='center',fontsize=8,weight='bold' if a==1 else 'normal')
 fig.canvas.draw();base=O/f'icon-examples-{theme}'
 require_matplotlib_panel_alignment(fig,json_out=str(base)+'.alignment.json',require_panel_labels=True,strict=True)
 fig.savefig(str(base)+'.pdf');fig.savefig(str(base)+'.svg',facecolor='none');fig.savefig(str(base)+'.png',dpi=600)
 plt.close(fig)
if __name__=='__main__':
 images=plates()
 for theme in ['light','dark']:draw(theme,images)
