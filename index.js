const express = require('express');
const bodyParser = require('body-parser');
const multer = require('multer');
const { spawn } = require('child_process');

const app = express();
const port = 3000;

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// 정적 파일 서비스 설정 -> 이거만 일단 바꿈
app.use(express.static('public'));

// Multer 설정 (업로드된 파일을 저장할 폴더 지정)
// multer.diskStorage --> 받은 파일을 어디에 저장할지, 어떤 이름으로 저장할지를 결정.
const storage = multer.diskStorage({
  destination: function (req, file, callback) {     // 저장 위치
    callback(null, 'public/');
  },
  filename: function (req, file, callback) {        // 저장 이름 ;file.originalname : 파일 이름 수정 없이 받은대로 저장
    callback(null, file.originalname);
  },
});

const upload = multer({ storage: storage });        // 미들웨어 설정 왼쪽의 storage<- 저장방식을 결정하는 multer 설정 객체
                                                    // 오른쪽의 storage <-- 위에서 설정한 (실제 사용할) storage 설정 객체


// 임시 홈 파일 전송                                
app.get('/', (req, res) => {
    res.sendFile(__dirname + '/public/upload.html');
});

// POST /upload 엔드포인트
app.post('/upload', upload.single('prescriptionImage'), (req, res) => {
  // 업로드된 파일 처리
  const filePath = req.file.path;

  // Python 모델 호출
  const pythonProcess = spawn('python', ['파이선파일 경로.py', filePath]);

  // Python 모델의 표준 출력 데이터 수신
  pythonProcess.stdout.on('data', (data) => {
    const resultText = data.toString().trim();

    // 결과를 Frontend로 전송
    res.json({ result: resultText });
  });

  // Python 모델의 표준 에러 출력 데이터 수신 (에러 처리)
  pythonProcess.stderr.on('data', (data) => {
    console.error(`Error: ${data}`);
    res.status(500).json({ error: 'Internal Server Error' });
  });
});

app.all("*", function (req, res) {
  res.status(404).send("<h1> 요청 페이지 없음 </h1>");
});

app.listen(port, () => {
  console.log(`http://localhost:3000`);
});
