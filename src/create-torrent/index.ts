import { writeFileSync } from "fs";
const createTorrent = require('create-torrent');

createTorrent(process.argv[2], {
    name: process.argv[4],
    comment: process.argv[5],
    createdBy: "Nyan Anime Toolkit",
    announceList: [
        "udp://tracker.nyananime.xyz:449",
        "wss://tracker.nyananime.xyz"
    ],
    onProgress: (done, length) => {
        process.stdout.write(`${((done / length) * 100).toFixed(2)}\n`);
    }
}, (err, torrent) => {
    if(err) {
        console.error(err);
        return;
    }

    writeFileSync(process.argv[3], torrent);
});
