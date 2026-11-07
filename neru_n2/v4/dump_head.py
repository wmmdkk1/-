import bpy, numpy as np, os
out=os.environ['DUMP']
h=bpy.data.objects['Head_new_PinkBraid']
np.save(out, np.array([(h.matrix_world@v.co)[:] for v in h.data.vertices],dtype=np.float32))
s=bpy.data.objects['model_part9']
np.save(out.replace('.npy','_shirt.npy'), np.array([(s.matrix_world@v.co)[:] for v in s.data.vertices],dtype=np.float32))
print('DUMP_OK')
