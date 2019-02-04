int cntr;

void setup() 
{
  Serial.begin(9600);
}

void loop() 
{
  Serial.print("Hello ");
  Serial.println(cntr);
  cntr++;
  delay(500);
}
