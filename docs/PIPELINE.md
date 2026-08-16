# Pipeline vidéo

```
CameraWorker → VideoWorker → InferenceWorker → Events/Alerts
```

Controllers : `desktop.controllers.video_pipeline_controller`  
AI backend : `backend.ai.manager.AIManager`

C++ :
```bash
export ONNXRUNTIME_ROOT=/path/to/onnxruntime
cd cpp_backend && cmake -B build -DONNXRUNTIME_ROOT=$ONNXRUNTIME_ROOT && cmake --build build
```
