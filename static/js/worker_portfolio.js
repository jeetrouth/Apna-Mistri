async function chatWithWorker(workerId){

   const res = await fetch("/chat/start",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify({workerId})
   })

   // USER NOT LOGGED IN
   if(res.status === 401){
      window.location.href = "/getstarted";
      return;
   }

   const data = await res.json()

   if(data.conversationId){
      window.location.href = `/inbox?cid=${data.conversationId}`
   }
}
async function hireWorker(workerId){

   const res = await fetch("/api/check-auth")

   if(res.status === 401){
      window.location.href = "/getstarted"
      return
   }

   window.location.href = `/create-job/${workerId}`
}