import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:barcode_scan/barcode_scan.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_nfc_reader/flutter_nfc_reader.dart';
import 'package:intl/intl.dart';

class DataPage extends StatefulWidget {
  ///MyHomePage({Key key, this.title}) : super(key: key);

  /// final String title;

  @override
  _DataPageState createState() => _DataPageState();
}

class _DataPageState extends State<DataPage> {
  //String _result = "Text";
  NfcData _nfcData;
  var _result = "Please Scan the QR code";

  static final dateFormat = new DateFormat('MMM d, yyyy hh:mm aaa');
  Map<String, dynamic> _response;
  Map<String, dynamic> responseTitles = {
    "name": "Room Name",
    "current_strength": "Current Strength",
    "max_capacity": "Max Capacity",
    "last_sanitized_time": "Last Sanitized Time",
  };
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
      _response = jsonDecode(utf8.decode(response.bodyBytes));
      if (_response['last_sanitized_time'] != null) {
        _response['last_sanitized_time'] =
            dateFormat.format(DateTime.parse(_response['last_sanitized_time']));
      }
    });
    print("State updated!");
    print(_response);
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
    }

    setState(() {
      _nfcData = response;
    });
  }

  Padding getTableElement(String value) {
    return Padding(
      padding: const EdgeInsets.all(15),
      child: Text(
        value,
        style: TextStyle(color: Colors.blue, fontSize: 20),
        textAlign: TextAlign.left,
      ),
    );
  }

  List<Widget> populateCard() {
    List<Widget> entryCard = new List<Widget>();
    if (_response == null) {
      entryCard.add(Image.network(
        'https://www.clipartkey.com/mpngs/m/229-2295584_qr-code-scan-hand-scan-qr-code-png.png',
        fit: BoxFit.fill,
      ));
    } else if (_response['code'] == 200) {
      entryCard.add(getTableElement("Thank you for scanning!"));
    } else {
      responseTitles.forEach(
          (k, v) => entryCard.add(getTableElement("$v : ${_response[k]}")));
    }
    return entryCard;
  }

  @override
  Widget build(BuildContext context) {
    print(_result);
    return Scaffold(
      appBar: AppBar(
          //title: Text(widget.title),
          ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text(
              'Response Text',
            ),
            Card(
              elevation: 10,
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: populateCard()),
            ),
            SizedBox(height: 50),
            RaisedButton.icon(
                color: Colors.blue,
                textColor: Colors.white,
                disabledColor: Colors.grey,
                disabledTextColor: Colors.black,
                padding: EdgeInsets.all(12.0),
                splashColor: Colors.blueAccent,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(25.0),
                ),
                onPressed: startNFC,
                label: Text(
                  "Scan",
                  style: TextStyle(fontFamily: 'Times New Roman', fontSize: 23),
                ),
                icon: Icon(Icons.camera_alt))
          ],
        ),
      ),
    );
  }
}
