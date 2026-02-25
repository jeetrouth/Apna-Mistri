document.addEventListener("DOMContentLoaded", function(){

  const stars = document.querySelectorAll(".stars span");
  let rating = 0;

  stars.forEach((star, index) => {

    star.addEventListener("click", function(){

      rating = index + 1;

      stars.forEach(s => s.classList.remove("active"));

      for(let i = 0; i < rating; i++){
        stars[i].classList.add("active");
      }

      console.log("Selected rating:", rating);

    });

  });

});