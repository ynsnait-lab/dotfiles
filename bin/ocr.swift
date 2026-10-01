// ocr — texte d'une image avec le moteur Vision d'Apple (français + anglais), hors ligne.
//   ocr image.png [autre.jpg…]   affiche le texte
//   ocr -c image.png             … et le copie dans le presse-papiers
//   ocr                          sélection d'une zone de l'écran → texte copié
// Compilé par install.sh :  swiftc -O ~/dotfiles/bin/ocr.swift -o ~/.local/bin/ocr
import AppKit
import Foundation
import Vision

var copy = false
var files: [String] = []
for a in CommandLine.arguments.dropFirst() {
    if a == "-c" { copy = true } else { files.append(a) }
}

if files.isEmpty {
    let tmp = NSTemporaryDirectory() + "ocr-\(getpid()).png"
    let cap = Process()
    cap.executableURL = URL(fileURLWithPath: "/usr/sbin/screencapture")
    cap.arguments = ["-i", "-x", tmp]
    try? cap.run()
    cap.waitUntilExit()
    guard FileManager.default.fileExists(atPath: tmp) else { exit(1) }  // sélection annulée
    files = [tmp]
    copy = true
}

var blocks: [String] = []
for f in files {
    guard let img = NSImage(contentsOfFile: f),
          let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        FileHandle.standardError.write("ocr : image illisible : \(f)\n".data(using: .utf8)!)
        continue
    }
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.usesLanguageCorrection = true
    req.recognitionLanguages = ["fr-FR", "en-US"]
    try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
    let lines = (req.results ?? []).compactMap { $0.topCandidates(1).first?.string }
    blocks.append(lines.joined(separator: "\n"))
}

let text = blocks.joined(separator: "\n\n")
print(text)
if copy && !text.isEmpty {
    NSPasteboard.general.clearContents()
    NSPasteboard.general.setString(text, forType: .string)
}
