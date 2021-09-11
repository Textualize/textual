/*
 * Easing functions from http://easings.net;
 * This script generates the data points used to test the _easing.py functions.
 */

function easeInSine(x: number): number {
    return 1 - cos((x * PI) / 2);
}

function easeOutSine(x: number): number {
    return sin((x * PI) / 2);
}

function easeInOutSine(x: number): number {
    return -(cos(PI * x) - 1) / 2;
}


function easeInQuad(x: number): number {
    return x * x;
}

function easeOutQuad(x: number): number {
    return 1 - (1 - x) * (1 - x);
}

function easeInOutQuad(x: number): number {
    return x < 0.5 ? 2 * x * x : 1 - pow(-2 * x + 2, 2) / 2;
}


function easeInCubic(x: number): number {
    return x * x * x;
}

function easeOutCubic(x: number): number {
    return 1 - pow(1 - x, 3);
}

function easeInOutCubic(x: number): number {
    return x < 0.5 ? 4 * x * x * x : 1 - pow(-2 * x + 2, 3) / 2;
}


function easeInQuart(x: number): number {
    return x * x * x * x;
}

function easeOutQuart(x: number): number {
    return 1 - pow(1 - x, 4);
}

function easeInOutQuart(x: number): number {
    return x < 0.5 ? 8 * x * x * x * x : 1 - pow(-2 * x + 2, 4) / 2;
}


function easeInQuint(x: number): number {
    return x * x * x * x * x;
}

function easeOutQuint(x: number): number {
    return 1 - pow(1 - x, 5);
}

function easeInOutQuint(x: number): number {
    return x < 0.5 ? 16 * x * x * x * x * x : 1 - pow(-2 * x + 2, 5) / 2;
}


function easeInExpo(x: number): number {
    return x === 0 ? 0 : pow(2, 10 * x - 10);
}

function easeOutExpo(x: number): number {
    return x === 1 ? 1 : 1 - pow(2, -10 * x);
}

function easeInOutExpo(x: number): number {
    return x === 0
      ? 0
      : x === 1
      ? 1
      : x < 0.5 ? pow(2, 20 * x - 10) / 2
      : (2 - pow(2, -20 * x + 10)) / 2;
}


function easeInCirc(x: number): number {
    return 1 - sqrt(1 - pow(x, 2));
}

function easeOutCirc(x: number): number {
    return sqrt(1 - pow(x - 1, 2));
}

function easeInOutCirc(x: number): number {
    return x < 0.5
      ? (1 - sqrt(1 - pow(2 * x, 2))) / 2
      : (sqrt(1 - pow(-2 * x + 2, 2)) + 1) / 2;
}


function easeInBack(x: number): number {
    const c1 = 1.70158;
    const c3 = c1 + 1;

    return c3 * x * x * x - c1 * x * x;
}

function easeOutBack(x: number): number {
    const c1 = 1.70158;
    const c3 = c1 + 1;

    return 1 + c3 * pow(x - 1, 3) + c1 * pow(x - 1, 2);
}

function easeInOutBack(x: number): number {
    const c1 = 1.70158;
    const c2 = c1 * 1.525;

    return x < 0.5
      ? (pow(2 * x, 2) * ((c2 + 1) * 2 * x - c2)) / 2
      : (pow(2 * x - 2, 2) * ((c2 + 1) * (x * 2 - 2) + c2) + 2) / 2;
}


function easeInElastic(x: number): number {
    const c4 = (2 * Math.PI) / 3;

    return x === 0
      ? 0
      : x === 1
      ? 1
      : -pow(2, 10 * x - 10) * sin((x * 10 - 10.75) * c4);
}

function easeOutElastic(x: number): number {
    const c4 = (2 * Math.PI) / 3;

    return x === 0
      ? 0
      : x === 1
      ? 1
      : pow(2, -10 * x) * sin((x * 10 - 0.75) * c4) + 1;
}

function easeInOutElastic(x: number): number {
    const c5 = (2 * Math.PI) / 4.5;

    return x === 0
      ? 0
      : x === 1
      ? 1
      : x < 0.5
      ? -(pow(2, 20 * x - 10) * sin((20 * x - 11.125) * c5)) / 2
      : (pow(2, -20 * x + 10) * sin((20 * x - 11.125) * c5)) / 2 + 1;

}


function easeInBounce(x: number): number {
    return 1 - easeOutBounce(1 - x);
}

function easeOutBounce(x: number): number {
    const n1 = 7.5625;
    const d1 = 2.75;

    if (x < 1 / d1) {
        return n1 * x * x;
    } else if (x < 2 / d1) {
        return n1 * (x -= 1.5 / d1) * x + 0.75;
    } else if (x < 2.5 / d1) {
        return n1 * (x -= 2.25 / d1) * x + 0.9375;
    } else {
        return n1 * (x -= 2.625 / d1) * x + 0.984375;
    }
}

function easeInOutBounce(x: number): number {
    return x < 0.5
      ? (1 - easeOutBounce(1 - 2 * x)) / 2
      : (1 + easeOutBounce(2 * x - 1)) / 2;
}


const funcs = [
    easeInSine, easeOutSine, easeInOutSine, easeInQuad, easeOutQuad, easeInOutQuad,
    easeInCubic, easeOutCubic, easeInOutCubic, easeInQuart, easeOutQuart, easeInOutQuart,
    easeInQuint, easeOutQuint, easeInOutQuint, easeInExpo, easeOutExpo, easeInOutExpo,
    easeInCirc, easeOutCirc, easeInOutCirc, easeInBack, easeOutBack, easeInOutBack,
    easeInElastic, easeOutElastic, easeInOutElastic, easeInBounce, easeOutBounce, easeInOutBounce
];

const points = [
    0.0,
    0.05,
    0.1,
    0.15,
    0.2,
    0.25,
    0.3,
    0.35,
    0.4,
    0.45,
    0.5,
    0.55,
    0.6,
    0.65,
    0.7,
    0.75,
    0.8,
    0.85,
    0.9,
    0.95,
    1.0
];

let PI = Math.PI;
let cos = Math.cos;
let sin = Math.sin;
let pow = Math.pow;
let sqrt = Math.sqrt;

for (func of funcs) {
    console.log(func.name);
    let values = [];
    for (point of points) {
        values.push(func(point));
    }
    console.log(values);
}
