console.log("Gesture extension injected");

// Create video preview
const video = document.createElement("video");
video.style.position = "fixed";
video.style.bottom = "10px";
video.style.right = "10px";
video.style.width = "240px";
video.autoplay = true;
video.playsInline = true;
video.muted = true;

document.body.appendChild(video);

// Check API support
if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
  console.error("getUserMedia NOT supported");
  alert("Camera API not supported on this page");
} else {
  navigator.mediaDevices
    .getUserMedia({ video: true })
    .then((stream) => {
      console.log("Camera stream obtained:", stream);
      video.srcObject = stream;
    })
    .catch((err) => {
      console.error("CAMERA ERROR NAME:", err.name);
      console.error("CAMERA ERROR MESSAGE:", err.message);
      console.error(err);
      alert("Camera error: " + err.name);
    });
}
