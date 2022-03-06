import { readFileSync, writeFileSync } from "fs";

/*  Cleans up .VTT subtitles from
    - m transforms
    - \h characters
    - unnecessary empty lines
    - same timestamps with different subtitles
    - same subtitles with different timestamps */

const tRegex = new RegExp("(\\d\\d:\\d\\d.\\d\\d\\d) --> (\\d\\d:\\d\\d.\\d\\d\\d)", "gm");
const mRegex = new RegExp("m ((\\d|-)+?(?= ))(.*)", "gm");

const input = readFileSync(process.argv[2]).toString();
const lines = input.split("\n");

let lastTimestamp = "";
let currTimestamp = "";
let lastLines: string[] = [];
let currLines: string[] = [];
const outLines = lines.reduce((acc, curr) => {
    if(tRegex.test(curr)) {
        lastTimestamp = currTimestamp;
        currTimestamp = curr;

        if(lastTimestamp != currTimestamp) {
            if(acc[acc.length - 1] != "") { acc.push(""); }
            acc.push(curr);

            if(currLines.length > 0 && currLines.length == lastLines.length && currLines.every((e, i) => e == lastLines[i])) {
                acc = acc.slice(0, -currLines.length - 2);
            }

            lastLines = currLines;
            currLines = [];
        }
    } else if(mRegex.test(curr)) {
        acc = acc.slice(0, -2);
    } else if(lastTimestamp != currTimestamp && curr != "") {
        acc.push(curr);
        currLines.push(curr);
    }
    
    return acc;
}, ["WEBVTT"]);
let output = outLines.join("\n");
output = output.split("\\h").join("");

writeFileSync(process.argv[3], output);