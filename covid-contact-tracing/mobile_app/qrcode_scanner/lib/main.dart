import 'dart:math';

import 'package:flutter/material.dart';

///import 'data.dart';

import 'dart:convert';

import 'package:barcode_scan/barcode_scan.dart';
import 'package:flutter/services.dart';
import 'package:http/http.dart' as http;

import 'package:flutter_nfc_reader/flutter_nfc_reader.dart';
import 'package:intl/intl.dart';

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
        primarySwatch: generateMaterialColor(Palette.primary),
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: MyHomePage(title: 'Covid Contact Tracing'),
    );
  }
}

MaterialColor generateMaterialColor(Color color) {
  return MaterialColor(color.value, {
    50: tintColor(color, 0.9),
    100: tintColor(color, 0.8),
    200: tintColor(color, 0.6),
    300: tintColor(color, 0.4),
    400: tintColor(color, 0.2),
    500: color,
    600: shadeColor(color, 0.1),
    700: shadeColor(color, 0.2),
    800: shadeColor(color, 0.3),
    900: shadeColor(color, 0.4),
  });
}

int tintValue(int value, double factor) =>
    max(0, min((value + ((255 - value) * factor)).round(), 255));

Color tintColor(Color color, double factor) => Color.fromRGBO(
    tintValue(color.red, factor),
    tintValue(color.green, factor),
    tintValue(color.blue, factor),
    1);

int shadeValue(int value, double factor) =>
    max(0, min(value - (value * factor).round(), 255));

Color shadeColor(Color color, double factor) => Color.fromRGBO(
    shadeValue(color.red, factor),
    shadeValue(color.green, factor),
    shadeValue(color.blue, factor),
    1);

class Palette {
  static const Color primary = Color(0xFF1A237E);
}

class MyHomePage extends StatefulWidget {
  MyHomePage({Key key, this.title}) : super(key: key);

  final String title;

  @override
  _MyHomePageState createState() => new _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  NfcData _nfcData;
  var _result = "Please Tap on the NFC Tag";

  static final dateFormat = new DateFormat('MMM d, yyyy hh:mm aaa');
  Map<String, dynamic> _response;
  Map<String, dynamic> responseTitles = {
    "name": "Room Name",
    "current_strength": "Current Strength",
    "max_capacity": "Max Capacity",
    "last_sanitized_time": "Last Sanitized Time",
  };

  get green => null;

  Future<http.Response> _sendRequest() async {
    String room_id, status;
    if (_result.contains("-")) {
      room_id = _result.split('-')[0];
      status = _result.split('-')[1];
      print("sending request to server with room_id and status as " +
          room_id +
          " & " +
          status);
    } else {
      room_id = '';
      status = 'denied';
    }

    http.Response response = await http.post(
      'http://192.168.0.10:5000/addEvent',
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(<String, String>{
        'user_id': '123456',
        'room_id': room_id,
        'status': status,
        'timestamp': new DateTime.now().millisecondsSinceEpoch.toString()
      }),
    );
    setState(() {
      _result = response.body;
      print(_result);
      _response = jsonDecode(utf8.decode(response.bodyBytes));
      _response = jsonDecode(_result);
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
        style: TextStyle(color: Colors.indigo[900], fontSize: 20),
        textAlign: TextAlign.left,
      ),
    );
  }

  List<Widget> populateCard() {
    List<Widget> entryCard = new List<Widget>();
    if (_response == null) {
      entryCard.add(Image.network(
        'https://images.unsplash.com/photo-1588771997195-ae313583be04?ixlib=rb-1.2.1&q=80&fm=jpg&crop=entropy&cs=tinysrgb&dl=united-nations-covid-19-response-1nhikKi0XNk-unsplash.jpg',
        fit: BoxFit.fill,
      ));
    } else if (_response['code'] == 200) {
      entryCard.add(getTableElement("Thank you for scanning. Stay safe!!"));
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
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text(
              'Please Tap on the NFC tag',
              style: TextStyle(fontSize: 16, color: green),
            ),
            Card(
              elevation: 10,
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: populateCard()),
            ),
            SizedBox(height: 2),
            RaisedButton.icon(
                color: Colors.indigo[900],
                textColor: Colors.white,
                disabledColor: Colors.grey,
                disabledTextColor: Colors.black,
                padding:
                    EdgeInsets.only(top: 12.0, left: 15, right: 15, bottom: 12),
                splashColor: Colors.blueAccent,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(25.0),
                ),
                onPressed: _scanQR,
                label: Text(
                  "Scan",
                  style: TextStyle(fontFamily: 'Times New Roman', fontSize: 18),
                ),
                icon: Icon(Icons.nfc_outlined))
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
          icon: Icon(Icons.camera_alt),
          label: Text(
            "Scan",
            style: TextStyle(fontFamily: 'Times New Roman', fontSize: 18),
          ),
          onPressed: startNFC),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
    );
  }
}
