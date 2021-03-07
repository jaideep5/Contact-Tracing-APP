import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:barcode_scan/barcode_scan.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;

import 'package:flutter_nfc_reader/flutter_nfc_reader.dart';

void main() {
  runApp(MyApp());
} /*  */

class MyApp extends StatelessWidget {
  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: MyHomePage(title: 'Covid Contact Tracing'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  MyHomePage({Key key, this.title}) : super(key: key);

  final String title;

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  String _result = "Text";
  NfcData _nfcData;

  Future<http.Response> _sendRequest() async {
    String room_id, status;
    if (_result.contains("-")) {
      room_id = _result.split('-')[0];
      status = _result.split('-')[1];
      print("sending request to server with room_id and status as " +
          room_id +
          " & " +
          status);
    }

    http.Response response = await http.post(
      'http://192.168.0.10:5000/addEvent',
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(<String, String>{
        'user_id': '1234567',
        'room_id': room_id,
        'status': status,
        'timestamp': new DateTime.now().millisecondsSinceEpoch.toString()
      }),
    );
    setState(() {
      _result = response.body;
    });
  }

  Future _scanQR() async {
    try {
      var qrResult = await BarcodeScanner.scan();
      setState(() {
        _result = qrResult.rawContent;
        _sendRequest();
      });
    } on PlatformException catch (e) {
      if (e.code == BarcodeScanner.cameraAccessDenied) {
        setState(() {
          _result = "Camera permission denied!";
        });
      }
    }
  }

  Future<void> startNFC() async {
    NfcData response;

    setState(() {
      _nfcData = NfcData();
      _nfcData.status = NFCStatus.reading;
    });

    print('NFC: Scan started');

    try {
      print('NFC: Scan readed NFC tag');
      response = await FlutterNfcReader.read();
    } on PlatformException {
      print('NFC: Scan stopped exception');
    }
    setState(() {
      _nfcData = response;
      _result = response != null ? response.content.substring(7) : null;
      _sendRequest();
    });
  }

  Future<void> stopNFC() async {
    NfcData response;

    try {
      print('NFC: Stop scan by user');
      response = await FlutterNfcReader.stop();
    } on PlatformException {
      print('NFC: Stop scan exception');
      response = NfcData(
        id: '',
        content: '',
        error: 'NFC scan stop exception',
        statusMapper: '',
      );
      response.status = NFCStatus.error;
      ;
    }

    setState(() {
      _nfcData = response;
    });
  }

  @override
  Widget build(BuildContext context) {
    print(_result);
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text(
              'Response Text',
            ),
            Text(
              '$_result',
              style: Theme.of(context).textTheme.headline4,
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
          icon: Icon(Icons.camera_alt),
          label: Text("Scan"),
          onPressed: startNFC),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
    );
  }
}
