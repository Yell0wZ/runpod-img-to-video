# Stable Video Diffusion RunPod Serverless

This project provides a RunPod serverless endpoint for Stable Video Diffusion img2vid-xt model.

## Features

- Generate videos from input images using Stable Video Diffusion
- Configurable generation parameters
- Input validation and error handling
- Optimized for GPU inference
- Base64 input/output format

## API Usage

### Input Format

Send a POST request with the following JSON structure:

```json
{
  "input": {
    "image": "base64_encoded_image_string",
    "num_frames": 25,
    "num_inference_steps": 25,
    "fps": 6,
    "motion_bucket_id": 127,
    "noise_aug_strength": 0.02,
    "seed": 42
  }
}
```

### Parameters

- `image` (required): Base64 encoded image string
- `num_frames` (optional, default: 25): Number of frames to generate (14-50)
- `num_inference_steps` (optional, default: 25): Number of denoising steps (1-50)
- `fps` (optional, default: 6): Frames per second for output video (1-30)
- `motion_bucket_id` (optional, default: 127): Controls motion amount (1-255)
- `noise_aug_strength` (optional, default: 0.02): Noise augmentation strength (0-1)
- `seed` (optional): Random seed for reproducible results

### Output Format

```json
{
  "video": "base64_encoded_mp4_video",
  "num_frames": 25,
  "fps": 6,
  "seed": 42
}
```

### Error Response

```json
{
  "error": "Error description"
}
```

## Deployment

1. Build the Docker image:
```bash
docker build -t stable-video-diffusion .
```

2. Deploy to RunPod:
   - Create a new serverless endpoint on RunPod
   - Use the built Docker image
   - Configure GPU settings (recommended: RTX 4090 or A100)
   - Set environment variables if needed

## Example Usage

### Python

```python
import requests
import base64

# Encode your image
with open("input_image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

# Make request
response = requests.post(
    "YOUR_RUNPOD_ENDPOINT_URL",
    json={
        "input": {
            "image": image_data,
            "num_frames": 25,
            "fps": 8,
            "seed": 123
        }
    }
)

result = response.json()

# Save output video
if "video" in result:
    video_data = base64.b64decode(result["video"])
    with open("output_video.mp4", "wb") as f:
        f.write(video_data)
```

### JavaScript

```javascript
// Encode image to base64
const imageBase64 = await fetch('input_image.jpg')
  .then(r => r.blob())
  .then(blob => new Promise(resolve => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result.split(',')[1]);
    reader.readAsDataURL(blob);
  }));

// Make request
const response = await fetch('YOUR_RUNPOD_ENDPOINT_URL', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    input: {
      image: imageBase64,
      num_frames: 25,
      fps: 8
    }
  })
});

const result = await response.json();

// Handle result
if (result.video) {
  // Create download link for video
  const videoBlob = new Blob([
    Uint8Array.from(atob(result.video), c => c.charCodeAt(0))
  ], { type: 'video/mp4' });
  
  const url = URL.createObjectURL(videoBlob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'generated_video.mp4';
  a.click();
}
```

## Performance Notes

- First request may take longer due to model loading
- Subsequent requests will be faster due to model caching
- Higher frame counts and inference steps increase processing time
- GPU memory usage scales with frame count

## Configuration

Edit `config.py` to modify:
- Model caching settings
- Default parameters
- Memory optimization options
- Validation limits