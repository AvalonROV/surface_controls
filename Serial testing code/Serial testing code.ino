int analog_pin = A0;
long thrusters[] = {50, 60 , 70 , 80 , 90 , 40};
int data = 0;
int thruster1_value = 50;
int thruster2_value = 60;
int thruster3_value = 70;
int thruster4_value = 80;
int thruster5_value = 90;
int thruster6_value = 40;
int Temprature = 36;
int ph ;
char userInput;


void setup(){
    Serial.begin(9600);
}

void loop(){
if(Serial.available() > 0){
    userInput = Serial.read();
    switch(userInput){
      case 'g':
        data = analogRead(analog_pin);
        Serial.println(data);
        break;
      case 'T':
        for(int i = 0; i < 5; i++){
          Serial.println(thrusters[i]);
        }
        
        break;
      case 's':
        num = serial.read()
        Serial.println(thrusters[num])
      default:
        Serial.println(data);
      break;
        
    }

}
}