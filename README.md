# carpool-multiagents

Muliagent system that models a carpooling system in a city with one-way streets. Both the vehicles and the passengers have an initial position and a destination. The objective is to have all of them reach their destination, by reducing the amount of car movements. 

This system is deployed in an IBM Cloud Foundry instance. A Flask server serializes the state of all agents at each tick of the system and sends it to Unity for visualization. The Mesa embedded server was also used for 2D visualization. 

## Simulation

Several tests were done to benchmark the model. In the experiments, the independent variables were the number of cars and passengers. First, a control test in which all of the agents were vehicles and there were no passengers was executed. This is the no-carpool situation. Then, the number of passengers increased, while reducing the number of vehicles in such a way that the sum of passengers and vehicles remained constant. The number of total car movements was measured in each experiment.

It turned out that the number of car movements was minimized when the vehicles were used to the most of their capacity (Experiment B), this is when there were around five passengers per car. The reduction in car movements was consistently of at least 10% when compared with the no carpool model (Experiment A). 

The drawback is that the total time taken for every car and passenger to reach their destination increased, altough this is expected even in the real world given the passenger waiting times, and the car deviation from optimal route if it did not have to pick and drop other passengers. 

The following table shows both experiments. 

|  Experiment A: No carpooling | Experiment B: Carpooling with 1:5 car-vehicle ratio |
|---|---|
| ![](https://github.com/E1-CarpoolProject/carpool-multiagents/blob/master/examples/no_carpool.gif) |  ![](https://github.com/E1-CarpoolProject/carpool-multiagents/blob/master/examples/carpool.gif) |


These visualizations use the embedded server in the Mesa package. The aspect of each agent was customized. At the beginning, every passenger starts with the left hand up, like asking for a ride. When they are dropped at their final destination, they have their hands down. After a vehicle has dropped its passengers and there are no more left to pick up, it goes to its final destination and disappears. 

**Note**: If you want to visualize the models in a better way, you can clone this repo and execute `python3 main.py`. This command will start the Mesa server so that you can play around with the parameters and watch different simulations!

## Agents Modeling 

Three different cateogories of agents were considered for the multi-agent modeling. Passive agents do not have goals, and mostly represent constraints in the system. Active agents have simple goals that don´t require a complex decision. Finally, cognitive agents have the most complex objectives, that require computations and usually algorithms. 

The following table shows the agents considered in this system: 

| Agent | Type  |  Objective |
|---|---|---|
|  Sidewalk | Passive  | Enforces the constraint that a Passenger may only have this kind of slot as starting point and destination. This means it can only appear and be dropped to the side of the road. |
| Road  |  Passive |  Enforces the constraint that a Car can only move trough this type of slot. It also enforces a direction constraint. |
| Traffic Light |  Passive | Similar to road agent, since Car can pass trough it. However, it does not have a fixed direction. It is not active because it does not control the state of the lights by itself, it only tells the car wheter it can pass.  |
|  Intersection | Active  | Has the simple objective of managing the state of the traffic lights that are involved in a crossroad  |
|  Passenger | Active  | This agent's objective is to reach its final destination. It only has to choose which vehicle can reach it sooner and select it for the ride. Since the vehicle already provides this information, it only has to do a simple comparison. |
| Car  | Cognitive  | This is the most complex agent of the system. It has to take both long term (next objective) and immediate decisions (which slot to move next). It must also scan the map to determine which is the nearest waiting passenger or drop-off point in case it has reached its current objective, and take an optimal decision. BFS is used for the search since A* does not provide additional optmality given the single way streets.  |

The following class diagram describes the different agents and their relationships: 

![](https://github.com/E1-CarpoolProject/carpool-multiagents/blob/master/examples/class.png)

## Agents Behaviour

The different type of agents must work together to reach a common objective: make every passenger and vehicle reach their destination. They also enforce some constraints on one another that have to be addressed. For example, the ´Intersection´ agent sets the state of the `TrafficLight`, which in turn, along with `Road` determine if `Car` can move to a certain slot. Not two `Car` agents can move to the same slot at the same time, to avoid collisions. There must be a one-to-one agreement between a `Car` and `Passenger` that is waiting for pickup, to avoid two vehicles trying to go for the same passenger. 

All of these constraints indicate that there must be a sequential process in each turn. Some actions and checks should be verified before taking some decisions. The ´CarpoolModel´ class is in charge of orchestrating the model. A simple tick will not work in this case, since the `Mesa` package does not provide a way to execute the turn for some type of agents before other types. This is necessary for the `TrafficLight`, for instance, whose state must be updated before the car moves. 

As a result, a `StagedActivation` was chosen for the model, which allows to partition the tick into several subturns that are executed in order. All of the agents must implement all of the fractions, but they don´t need to perform an actual action. Therefore, the turn works as follows: 

1. `notify_passenger`: Implemented for `Car`. If it does not have a current pickup objective, then pick the nearest `Passenger` using BFS and notify that this vehicle wants to pick it up, along with the distance between them. 
2. `confirm_car`: Implemented for `Passenger`. Once that it has received one or several notifications from `Car` agents, it should choose the one that is most near and confirm the vehicle to create the one-to-one relation. The other vehicles remain without pickup objective for the rest of this tick (but they may have a route nonetheless. 
3. `tick_traffic_lights`: Implemented for `Intersection`. Given the active time of each light and the current active counter, toggle the status of the `TrafficLight` agents if necessary. 
4. `move_cars`: Implemented for `Car`. Move the vehicle to the next corresponding slot. If there is a route, just move in the next direction. Otherwise, determine which is the optimal action: go for the pickup objective or drop any of the passengers onboard to their destinations. If there is no current pickup objective nor onboard passengers, move one slot in the direction of the destination. 
6. `pick_drop_passengers`: Implemented for `Car`. If the new slot is the pickup or drop-off point of a `Passenger`, change the state of the passenger and update the occupancy of the vehicle. 


The following secuence diagram describes the interaction protocols among the agents: 

![](https://github.com/E1-CarpoolProject/carpool-multiagents/blob/master/examples/protocols.png)


