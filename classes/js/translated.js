function computeA(n) {
  if (n === 0) {
    return 1;
  } else {
    return n * computeA(n - 1);
  }
}

// A recursive function that returns the factorial n

function checkB(text) {
  let i = 0;
  let j = text.length - 1;
  while (i < j) {
    if (text[i] !== text[j]) {
      return false;
    }
    i++;
    j--;
  }
  return true;
}

// A function that checks if the given string is a palindrome

function generateC(n) {
  let seq = [0, 1];
  for (let i = 2; i < n; i++) {
    seq.push(seq[seq.length - 1] + seq[seq.length - 2]);
  }
  return seq.slice(0, n);
}

// A function that returns a n long fibonacci sequence

function processD(n) {
  let total = 0;
  for (let i = 1; i < n + 1; i++) {
    if (i % 3 === 0 || i % 5 === 0) {
      total += i;
    }
  }
  return total;
}

// A function that returns the sum of the number under n dividable by 3 or 5

function computeE(n) {
  let result = [];
  for (let i = 1; i < n + 1; i++) {
    if (n % i === 0) {
      result.push(i);
    }
  }
  return result;
}

// A function that returns a list of numbers up to n that divide n

