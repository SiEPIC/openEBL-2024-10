''''
debugging strange KLayout cell name changes
'''


# configuration
tech_name = 'EBeam'
top_cell_name = 'EBeam_2024_10'
cell_Width = 605000
cell_Height = 410000
cell_Gap_Width = 8000
cell_Gap_Height = 8000
chip_Width = 8650000
chip_Height1 = 8490000
chip_Height2 = 8780000
br_cutout_x = 7484000
br_cutout_y = 898000
br_cutout2_x = 7855000
br_cutout2_y = 5063000
tr_cutout_x = 7037000
tr_cutout_y = 8494000

filename_out = 'EBeam'
layers_keep = ['1/0','1/10', '68/0', '81/0', '10/0', '99/0', '26/0', '31/0', '32/0', '33/0', '998/0']
layer_text = '10/0'
layer_SEM = '200/0'
layer_SEM_allow = ['edXphot1x', 'ELEC413','SiEPIC_Passives']  # which submission folder is allowed to include SEM images
layers_move = [[[31,0],[1,0]]] # move shapes from layer 1 to layer 2
dbu = 0.001
log_siepictools = False
framework_file = 'EBL_Framework_1cm_PCM_static.oas'
ubc_file = 'UBC_static.oas'

debug = True

# record processing time
import time
start_time = time.time()
from datetime import datetime
now = datetime.now()

# KLayout
import pya
from pya import *

# SiEPIC-Tools
import SiEPIC
from SiEPIC._globals import Python_Env, KLAYOUT_VERSION, KLAYOUT_VERSION_3
from SiEPIC.scripts import zoom_out, export_layout
from SiEPIC.utils import find_automated_measurement_labels
import os

def disable_libraries():
    print('Disabling KLayout libraries')
    for l in pya.Library().library_ids():
        print(' - %s' % pya.Library().library_by_id(l).name())
        pya.Library().library_by_id(l).delete()

#disable_libraries()

# path for this python file
path = os.path.dirname(os.path.realpath(__file__))

# Log file
global log_file
log_file = open(os.path.join(path,filename_out+'.txt'), 'w')
def log(text):
    global log_file
    log_file.write(text)
    log_file.write('\n')

log('SiEPIC-Tools %s, layout merge, running KLayout 0.%s.%s ' % (SiEPIC.__version__, KLAYOUT_VERSION,KLAYOUT_VERSION_3) )
current_time = now.strftime("%Y-%m-%d, %H:%M:%S local time")
log("Date: %s" % current_time)

# Load all the GDS/OAS files from the "submissions" folder:
files_in = [os.path.join(path,"../submissions","EBeam_openEBL_arunaPBS3_LC.gds")]


for f in [f for f in files_in if '.oas' in f.lower() or '.gds' in f.lower()]:
    basefilename = os.path.basename(f)

    # GitHub Action gets the actual time committed.  This can be done locally
    # via git restore-mtime.  Then we can load the time from the file stamp

    filedate = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y%m%d_%H%M")
    log("\nLoading: %s, dated %s" % (os.path.basename(f), filedate))

    # Tried to get it from GitHub but that didn't work:
    # get the time the file was last updated from the Git repository 
    # a = subprocess.run(['git', '-C', os.path.dirname(f), 'log', '-1', '--pretty=%ci',  basefilename], stdout = subprocess.PIPE) 
    # filedate = pd.to_datetime(str(a.stdout.decode("utf-8"))).strftime("%Y%m%d_%H%M")
    #filedate = os.path.getctime(os.path.dirname(f)) # .strftime("%Y%m%d_%H%M")
    
  
    # Load layout  
    layout2 = pya.Layout()
    layout2.read(f)

    # Debugging
    if debug:
        print('*** Cell names in layout %s, immediately after loading' % f)
        for c in layout2.each_cell():
            print(c.name)

    # Load layout  
    cv = pya.MainWindow().instance().load_layout(f)
    layout2 = cv.layout()
    
    # Debugging
    if debug:
        print('*** Cell names in layout %s, MainWindow load' % f)
        for c in layout2.each_cell():
            print(c.name + ' ' + c.basic_name())
            if c.basic_name() not in c.name:
                print('- warning: cell SNAME (basic_name = %s) does not match the cell name (name = %s)' % (c.name, c.basic_name()) )


log("\nExecution time: %s seconds" % int((time.time() - start_time)))

log_file.close()

# Display the layout in KLayout, using KLayout Package "klive", which needs to be installed in the KLayout Application
try:
    if Python_Env == 'Script':
        from SiEPIC.utils import klive
        klive.show(file_out, technology=tech_name)
except:
    pass

print("KLayout EBeam_merge.py, completed in: %s seconds" % int((time.time() - start_time)))


