// const myHeading = document.querySelector('h1');
// myHeading.textContent = 'Hello world!';

const myImage = document.querySelector('img');
myImage.onclick = () => {
  const mySrc = myImage.getAttribute('src');
  if (mySrc === 'images/95085656_p0.png') {
    myImage.setAttribute('src','images/00259767_p0.png');
  } else {
    myImage.setAttribute('src','images/95085656_p0.png');
  }
}

let myButton = document.querySelector('button');
let myHeading = document.querySelector('h1');

function setUserName() {
    let myName = prompt('Please enter your name.');
    if(!myName) {
      setUserName();
    } else {
      localStorage.setItem('name', myName);
      myHeading.innerHTML = 'Mozilla is cool, ' + myName + '!';
    }
  }
  
  if(!localStorage.getItem('name')) {
    setUserName();
  } else {
    let storedName = localStorage.getItem('name');
    myHeading.innerHTML = 'Mozilla is cool, ' + storedName + '!';
  }
  
  myButton.onclick = function() {
    setUserName();
  }