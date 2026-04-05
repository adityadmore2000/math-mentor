Problems processed but correct=False 
```
'{"problem_idx":{"count":11.0,"mean":2.5454545455,"std":1.8090680675,"min":0.0,"25%":2.0,"50%":2.0,"75%":4.0,"max":5.0},"temperature":{"count":11.0,"mean":0.2454545455,"std":0.1916436086,"min":0.0,"25%":0.1,"50%":0.2,"75%":0.4,"max":0.5},"latency_sec":{"count":11.0,"mean":422.1427272727,"std":65.9740600677,"min":223.45,"25%":439.705,"50%":440.05,"75%":444.305,"max":446.49},"thinking_length":{"count":11.0,"mean":10288.5454545455,"std":1495.8413260528,"min":6336.0,"25%":9897.0,"50%":10797.0,"75%":11103.5,"max":11915.0},"output_length":{"count":11.0,"mean":10761.2727272727,"std":1267.1189439756,"min":7479.0,"25%":10581.5,"50%":10806.0,"75%":11231.5,"max":12536.0}}'
```

Problems processed but correct=True
```
 '{"problem_idx":{"count":11.0,"mean":2.5454545455,"std":1.8090680675,"min":0.0,"25%":2.0,"50%":2.0,"75%":4.0,"max":5.0},"temperature":{"count":11.0,"mean":0.2454545455,"std":0.1916436086,"min":0.0,"25%":0.1,"50%":0.2,"75%":0.4,"max":0.5},"latency_sec":{"count":11.0,"mean":422.1427272727,"std":65.9740600677,"min":223.45,"25%":439.705,"50%":440.05,"75%":444.305,"max":446.49},"thinking_length":{"count":11.0,"mean":10288.5454545455,"std":1495.8413260528,"min":6336.0,"25%":9897.0,"50%":10797.0,"75%":11103.5,"max":11915.0},"output_length":{"count":11.0,"mean":10761.2727272727,"std":1267.1189439756,"min":7479.0,"25%":10581.5,"50%":10806.0,"75%":11231.5,"max":12536.0}}'
```


1) Thinking Length
- Correct ~6904
- Incorrect ~10288

  ![Chart](https://quickchart.io/chart?c={type:'pie',data:{labels:['Correct','Incorrect'],datasets:[{label:'Count',data:[6904,10288]}]}})


> Incorrect answers involve significantly longer reasoning traces

> The model tends to over-generate reasoning when it is confused or failing, rather than converging efficiently.

2) Latency Insight
- Incorrect ~422 sec
- Correct 269 sec

![Chart](https://quickchart.io/chart?c={type:'pie',data:{labels:['Correct','Incorrect'],datasets:[{label:'Count',data:[422,269]}]}})


### Data Distribution Analysis

- Model is overthinking when wrong
- Wrong reasoning = longer + inefficient inference

### The take
- We can't infer best parameter settings with 32 samples.

## Exploratory Data Analysis
