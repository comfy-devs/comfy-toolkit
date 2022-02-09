import { writeFileSync } from "fs";
const createTorrent = require('create-torrent');

console.log(process.argv);
createTorrent(process.argv[2], {
    name: process.argv[4],
    comment: process.argv[5],
    createdBy: "Nyan Anime Toolkit",
    announceList: [
        "udp://tracker.nyananime.xyz:449",
        "wss://tracker.nyananime.xyz"
    ]
}, (err, torrent) => {
    if(err) {
        console.error(err);
        return;
    }

    writeFileSync(process.argv[3], torrent);
});
