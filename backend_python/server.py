import grpc
from concurrent import futures
import time

# Import the generated classes
from generated import video_pb2
from generated import video_pb2_grpc

class VideoProcessor(video_pb2_grpc.VideoProcessorServicer):
    
    def ProcessVideo(self, request_iterator, context):
        print("Go Client Connected. Starting stream...")

        for frame in request_iterator:
            print(f"Received Frame: {len(frame.content)} bytes | TS: {frame.timestamp}")

            # --- YOUR LOGIC HERE ---
            # result = gesture_engine.predict(frame.content)
            # -----------------------

            # 2. SEND REPLY to Go
            # We mimic a result for now
            response = video_pb2.AnalysisResult(
                prediction="Peace Sign",
                confidence=0.95,
                timestamp=frame.timestamp
            )
            
            yield response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    video_pb2_grpc.add_VideoProcessorServicer_to_server(VideoProcessor(), server)
    
    # Listen on port 50051
    server.add_insecure_port('[::]:50051')
    print("Python gRPC Server running on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()