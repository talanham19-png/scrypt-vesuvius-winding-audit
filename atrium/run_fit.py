"""Run spiral-fitting's fit_spiral.py CLI unchanged, with cuDNN disabled (its sub-libraries are not installed)
and the peak CUDA memory reported at exit."""
import os, sys, runpy, atexit, time
import torch
torch.backends.cudnn.enabled = False
SPIRAL = os.environ["SPIRAL_DIR"]; sys.path.insert(0, SPIRAL); os.chdir(SPIRAL)
t0 = time.time()
def report():
    if torch.cuda.is_available():
        print(f"PEAK_VRAM_GB allocated={torch.cuda.max_memory_allocated()/2**30:.3f} reserved={torch.cuda.max_memory_reserved()/2**30:.3f} wall_s={time.time()-t0:.0f}", flush=True)
atexit.register(report)
sys.argv = ["fit_spiral.py"] + sys.argv[1:]
runpy.run_path(os.path.join(SPIRAL, "fit_spiral.py"), run_name="__main__")
