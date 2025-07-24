import base64
import io
from PIL import Image
from config import *

def validate_base64_image(base64_string):
    """Validate and decode base64 image string"""
    if not base64_string:
        raise ValueError("Image data is required")
    
    try:
        # Remove data URL prefix if present
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
        
        # Decode base64
        image_data = base64.b64decode(base64_string)
        
        # Validate it's a valid image
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    
    except Exception as e:
        raise ValueError(f"Invalid image data: {str(e)}")

def validate_generation_params(params):
    """Validate generation parameters"""
    validated = {}
    
    # Validate num_frames
    num_frames = params.get('num_frames', DEFAULT_NUM_FRAMES)
    if not isinstance(num_frames, int) or num_frames < MIN_NUM_FRAMES or num_frames > MAX_NUM_FRAMES:
        raise ValueError(f"num_frames must be an integer between {MIN_NUM_FRAMES} and {MAX_NUM_FRAMES}")
    validated['num_frames'] = num_frames
    
    # Validate num_inference_steps
    steps = params.get('num_inference_steps', DEFAULT_NUM_INFERENCE_STEPS)
    if not isinstance(steps, int) or steps < MIN_INFERENCE_STEPS or steps > MAX_INFERENCE_STEPS:
        raise ValueError(f"num_inference_steps must be an integer between {MIN_INFERENCE_STEPS} and {MAX_INFERENCE_STEPS}")
    validated['num_inference_steps'] = steps
    
    # Validate fps
    fps = params.get('fps', DEFAULT_FPS)
    if not isinstance(fps, (int, float)) or fps < MIN_FPS or fps > MAX_FPS:
        raise ValueError(f"fps must be a number between {MIN_FPS} and {MAX_FPS}")
    validated['fps'] = float(fps)
    
    # Validate motion_bucket_id
    motion_bucket_id = params.get('motion_bucket_id', DEFAULT_MOTION_BUCKET_ID)
    if not isinstance(motion_bucket_id, int) or motion_bucket_id < 1 or motion_bucket_id > 255:
        raise ValueError("motion_bucket_id must be an integer between 1 and 255")
    validated['motion_bucket_id'] = motion_bucket_id
    
    # Validate noise_aug_strength
    noise_strength = params.get('noise_aug_strength', DEFAULT_NOISE_AUG_STRENGTH)
    if not isinstance(noise_strength, (int, float)) or noise_strength < 0 or noise_strength > 1:
        raise ValueError("noise_aug_strength must be a float between 0 and 1")
    validated['noise_aug_strength'] = float(noise_strength)
    
    # Validate seed (optional)
    seed = params.get('seed')
    if seed is not None:
        if not isinstance(seed, int) or seed < 0:
            raise ValueError("seed must be a positive integer or null")
        validated['seed'] = seed
    else:
        validated['seed'] = None
    
    return validated

def validate_input(job_input):
    """Validate complete job input"""
    if not isinstance(job_input, dict):
        raise ValueError("Input must be a dictionary")
    
    # Validate required fields
    if 'image' not in job_input:
        raise ValueError("Missing required field: 'image'")
    
    # Validate image
    image = validate_base64_image(job_input['image'])
    
    # Validate generation parameters
    params = validate_generation_params(job_input)
    
    return image, params