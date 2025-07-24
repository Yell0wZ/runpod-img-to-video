import runpod
import torch
from diffusers import StableVideoDiffusionPipeline
from diffusers.utils import export_to_video
import base64
import tempfile
import os
import gc
from config import *
from validation import validate_input

# Global pipeline variable
pipeline = None

def load_model():
    """Load the Stable Video Diffusion model"""
    global pipeline
    if pipeline is None:
        print("Loading Stable Video Diffusion model...")
        
        # Configure torch dtype
        dtype = torch.float16 if TORCH_DTYPE == "float16" else torch.float32
        
        pipeline = StableVideoDiffusionPipeline.from_pretrained(
            MODEL_ID,
            torch_dtype=dtype,
            variant=VARIANT,
            cache_dir=CACHE_DIR
        )
        
        # Enable memory efficient attention if configured
        if ENABLE_MEMORY_EFFICIENT_ATTENTION:
            pipeline.enable_attention_slicing()
        
        # Move to GPU if available
        if torch.cuda.is_available():
            pipeline = pipeline.to("cuda")
            print(f"Model loaded on GPU: {torch.cuda.get_device_name()}")
            
            # Enable CPU offload if configured
            if ENABLE_CPU_OFFLOAD:
                pipeline.enable_model_cpu_offload()
        else:
            print("Model loaded on CPU")
    
    return pipeline


def encode_video_to_base64(video_path):
    """Encode video file to base64"""
    with open(video_path, "rb") as video_file:
        video_data = video_file.read()
        return base64.b64encode(video_data).decode('utf-8')

def handler(job):
    """RunPod serverless handler function"""
    try:
        job_input = job['input']
        
        # Validate input and get validated parameters
        print("Validating input...")
        image, params = validate_input(job_input)
        
        # Load model
        pipe = load_model()
        
        # Resize image to SVD requirements
        print("Preprocessing image...")
        image = image.resize((TARGET_WIDTH, TARGET_HEIGHT))
        
        # Set seed if provided
        generator = None
        if params['seed'] is not None:
            generator = torch.manual_seed(params['seed'])
        
        print(f"Generating video with {params['num_frames']} frames...")
        
        # Generate video frames
        frames = pipe(
            image, 
            decode_chunk_size=8, 
            generator=generator,
            motion_bucket_id=params['motion_bucket_id'],
            noise_aug_strength=params['noise_aug_strength'],
            num_frames=params['num_frames'],
            num_inference_steps=params['num_inference_steps']
        ).frames[0]
        
        # Create temporary file for video
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False, dir=TEMP_DIR) as tmp_file:
            video_path = tmp_file.name
        
        # Export frames to video
        print("Exporting video...")
        export_to_video(frames, video_path, fps=params['fps'])
        
        # Encode video to base64
        video_b64 = encode_video_to_base64(video_path)
        
        # Clean up
        os.unlink(video_path)
        
        # Clear GPU memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
        
        return {
            "video": video_b64,
            "num_frames": len(frames),
            "fps": params['fps'],
            "seed": params['seed']
        }
        
    except ValueError as e:
        return {"error": f"Validation error: {str(e)}"}
    except Exception as e:
        return {"error": f"Processing failed: {str(e)}"}

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})