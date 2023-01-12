import { writeFileSync } from "fs";
import createTorrent from "create-torrent";
import parseTorrent from "parse-torrent";
import MagnetUri from "magnet-uri";

createTorrent(process.argv[2], {
    name: process.argv[4],
    comment: process.argv[5],
    createdBy: "Comfy Toolkit",
    announceList: [[
        "wss://tracker.comfy.lamkas.dev:9102"
    ]],
    onProgress: (done, length) => {
        process.stdout.write(`progress=${((done / length) * 100).toFixed(2)}\n`);
    }
}, (err, torrent) => {
    if(err) {
        console.error(err);
        return;
    }
    writeFileSync(`${process.argv[3]}/series.torrent`, torrent);

    const parsedTorrent = parseTorrent(torrent);
    const uri = MagnetUri.encode(parsedTorrent);
    writeFileSync(`${process.argv[3]}/torrent.sql`, `INSERT IGNORE INTO torrents (id, magnet) VALUES ("${process.argv[4]}", "${uri}");`);
});
