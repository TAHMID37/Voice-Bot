// let isRecording = false;
// let socket;
// let microphone;

// const socket_port = 5001;
// socket = io(
//   "http://" + window.location.hostname + ":" + socket_port.toString()
// );

// socket.on("transcription_update", (data) => {
//   document.getElementById("captions").innerHTML = data.transcription;
// });

// async function getMicrophone() {
//   try {
//     const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//     return new MediaRecorder(stream, { mimeType: "audio/webm" });
//   } catch (error) {
//     console.error("Error accessing microphone:", error);
//     throw error;
//   }
// }

// async function openMicrophone(microphone, socket) {
//   return new Promise((resolve) => {
//     microphone.onstart = () => {
//       console.log("Client: Microphone opened");
//       document.body.classList.add("recording");
//       resolve();
//     };
//     microphone.ondataavailable = async (event) => {
//       console.log("client: microphone data received");
//       if (event.data.size > 0) {
//         socket.emit("audio_stream", event.data);
//       }
//     };
//     microphone.start(1000);
//   });
// }

// async function startRecording() {
//   isRecording = true;
//   microphone = await getMicrophone();
//   console.log("Client: Waiting to open microphone");
//   await openMicrophone(microphone, socket);
// }

// async function stopRecording() {
//   if (isRecording === true) {
//     microphone.stop();
//     microphone.stream.getTracks().forEach((track) => track.stop()); // Stop all tracks
//     socket.emit("toggle_transcription", { action: "stop" });
//     microphone = null;
//     isRecording = false;
//     console.log("Client: Microphone closed");
//     document.body.classList.remove("recording");
//   }
// }

// document.addEventListener("DOMContentLoaded", () => {
//   const recordButton = document.getElementById("record");

//   recordButton.addEventListener("click", () => {
//     if (!isRecording) {
//       socket.emit("toggle_transcription", { action: "start" });
//       startRecording().catch((error) =>
//         console.error("Error starting recording:", error)
//       );
//     } else {
//       stopRecording().catch((error) =>
//         console.error("Error stopping recording:", error)
//       );
//     }
//   });
// });


let isRecording = false;
let socket;
let microphone;
let audioElement;

const socket_port = 5001;
socket = io(
  "http://" + window.location.hostname + ":" + socket_port.toString()
);

socket.on("transcription_update", (data) => {
  document.getElementById("captions").innerHTML = data.transcription;
});

socket.on("tts_update", (data) => {
  document.getElementById("answers").innerHTML = data.response;
});

socket.on("tts_audio", (data) => {
  // Receive the audio URL from the server and play it
  const audioUrl = data.audio_url;
  console.log("Client: Received TTS audio URL:", audioUrl);

  // If there's already an audio element, stop and remove it
  if (audioElement) {
    audioElement.pause();
    audioElement.src = '';  // Clear the old src
    document.body.removeChild(audioElement);
  }

  // Create a new audio element and play the TTS output
  audioElement = new Audio(audioUrl);
  document.body.appendChild(audioElement);
  audioElement.play().then(() => {
    console.log("Client: Playing TTS audio");
  }).catch((error) => {
    console.error("Client: Error playing audio:", error);
  });
});

async function getMicrophone() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    return new MediaRecorder(stream, { mimeType: "audio/webm" });
  } catch (error) {
    console.error("Error accessing microphone:", error);
    throw error;
  }
}

async function openMicrophone(microphone, socket) {
  return new Promise((resolve) => {
    microphone.onstart = () => {
      console.log("Client: Microphone opened");
      document.body.classList.add("recording");
      resolve();
    };
    microphone.ondataavailable = async (event) => {
      console.log("Client: Microphone data received");
      if (event.data.size > 0) {
        socket.emit("audio_stream", event.data);
      }
    };
    microphone.start(1000);
  });
}

async function startRecording() {
  isRecording = true;
  microphone = await getMicrophone();
  console.log("Client: Waiting to open microphone");
  await openMicrophone(microphone, socket);
}

async function stopRecording() {
  if (isRecording === true) {
    microphone.stop();
    microphone.stream.getTracks().forEach((track) => track.stop()); // Stop all tracks
    socket.emit("toggle_transcription", { action: "stop" });
    microphone = null;
    isRecording = false;
    console.log("Client: Microphone closed");
    document.body.classList.remove("recording");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const recordButton = document.getElementById("record");

  recordButton.addEventListener("click", () => {
    if (!isRecording) {
      socket.emit("toggle_transcription", { action: "start" });
      startRecording().catch((error) =>
        console.error("Error starting recording:", error)
      );
    } else {
      stopRecording().catch((error) =>
        console.error("Error stopping recording:", error)
      );
    }
  });
});
