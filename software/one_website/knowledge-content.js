"use strict";
/* Original teaching syntheses grounded in reviewed Principia source documents.
 * Text here is educational commentary, not a promoted canonical review artifact. */
(function(root,factory){const api=factory();if(typeof module==="object"&&module.exports)module.exports=api;root.PrincipiaKnowledge=api;})(typeof globalThis!=="undefined"?globalThis:this,function(){
const topics=[
  {
    "id": "systems",
    "domain": "Foundations",
    "title": "Where does a system begin?",
    "question": "What exactly are we studying?",
    "lead": "Every explanation starts by drawing a boundary. The same refrigerator can be a cold cabinet, a heat pump, or a device in a heated room; the useful answer changes with the boundary.",
    "formula": "Inputs → [system boundary + stored state] → outputs",
    "example": "A refrigerator keeps its cabinet cold by moving heat into the room. Include only the cabinet and cooling removes energy; include the whole room and its electricity supply and the accounting looks different.",
    "sections": [
      {
        "heading": "Choose the question before the boundary",
        "text": "A system is a selected set of components and interactions. A boundary decides which processes count as internal and which enter as external influences. Boundaries are analytic choices, not invisible physical walls. The right one depends on the question you are trying to answer.",
        "thought": "Draw two boundaries around one appliance. What energy crosses each?"
      },
      {
        "heading": "Inside the boundary",
        "text": "Identify stored quantities (temperature, fluid volume, queued requests), incoming flows and outgoing flows. Ask who or what controls each flow. A correct box diagram is more useful than an elaborate picture that omits the governing transfers.",
        "thought": "Find one store, one inflow and one outflow in a household example."
      },
      {
        "heading": "Why the same system has many models",
        "text": "A heat-transfer model tracks watts and temperature; a reliability model tracks failure rates, maintenance and time. Neither is the whole refrigerator. The simplifying assumptions can be justified for one question and unacceptable for another.",
        "thought": "What does an electrical-safety question require that a temperature model ignores?"
      },
      {
        "heading": "Use boundaries to diagnose failure",
        "text": "When an output seems impossible, look for an omitted path: hidden power, leakage, a retry loop, a second user group or an overlooked reservoir. Before inventing a complicated explanation, check whether the diagram contains all significant exchanges.",
        "thought": "Which omitted input could make a simple model overpredict performance?"
      }
    ],
    "misconception": "A system boundary is not a claim that everything beyond it is unimportant.",
    "check": {
      "question": "What happens if you expand the boundary around a refrigerator to include its room?",
      "choices": [
        "The heat and electrical work must be accounted for within a larger energy budget",
        "The compressor stops using electricity",
        "The refrigerator violates energy conservation"
      ],
      "answer": 0,
      "explanation": "The larger boundary now includes the room's energy flows and the appliance's heat rejection; no energy is created by the change of boundary."
    },
    "links": [
      "conservation",
      "stocks",
      "models"
    ],
    "lab": "/learn/refrigerator/",
    "source": "https://github.com/Rhodan-lab/principle-to-system/blob/main/concepts/systems-and-models.md"
  },
  {
    "id": "conservation",
    "domain": "Foundations",
    "title": "Conservation is the first audit",
    "question": "Where can the missing quantity have gone?",
    "lead": "A sound system model is constrained by accounting. Conservation does not tell you all the mechanisms, but it rules out claims that create water or energy from nowhere.",
    "formula": "Final store = Initial store + Inflow − Outflow + generated − consumed",
    "example": "Capture 640 L, serve 90 L, spill nothing, and begin empty: 550 L remains. If a report shows 700 L, its accounts cannot all be right.",
    "sections": [
      {
        "heading": "Account before you optimize",
        "text": "Start with a clearly defined quantity and consistent units. Liquid water in a nonreacting tank is tracked by volume; electrical energy in a battery by kWh; incoming requests by count. For energy, distinguish transfers across the boundary from transformations inside it.",
        "thought": "What exactly is conserved in your example: energy, mass, charge, or counted requests?"
      },
      {
        "heading": "Track every path",
        "text": "A reservoir has rainwater inflow, use and overflow. A battery has charge and discharge flows plus conversion losses. A bounded queue has arriving, served, queued and rejected requests. The names differ but each model must reconcile its accounting.",
        "thought": "Sketch the flow ledger of a rainwater tank."
      },
      {
        "heading": "Understand the residual",
        "text": "A residual is the discrepancy between the left and right sides of an accounting equality. In a working synthetic model it should be zero up to numerical tolerance. In measurements, a nonzero residual may indicate uncertainty, sensor drift, omitted flows, or inconsistent boundaries.",
        "thought": "Does a nonzero residual prove new physics? Why not?"
      },
      {
        "heading": "Conservation is not enough",
        "text": "A conserved amount may become inaccessible or unusable. Water stored in the wrong place cannot serve a needed user; energy dispersed at near-uniform temperature cannot all become useful work. The timing and quality of a resource matter alongside its quantity.",
        "thought": "A battery can conserve energy yet fail a load. Identify the constraint."
      }
    ],
    "misconception": "Conservation by itself does not guarantee that the stored resource can serve the intended demand.",
    "check": {
      "question": "A tank starts with 100 L, captures 60 L, serves 90 L and has no overflow. What remains?",
      "choices": [
        "250 L",
        "70 L",
        "160 L"
      ],
      "answer": 1,
      "explanation": "100 + 60 − 90 = 70 liters. All volume terms use the same units and time interval."
    },
    "links": [
      "systems",
      "stocks",
      "water"
    ],
    "lab": "/explore/rainwater/",
    "source": "https://github.com/Rhodan-lab/principle-to-system/blob/main/concepts/energy-and-matter.md"
  },
  {
    "id": "units",
    "domain": "Mathematics",
    "title": "Units reveal hidden mistakes",
    "question": "Do these numbers even describe the same thing?",
    "lead": "A number becomes physically meaningful through its quantity and unit. Dimensional reasoning often catches mistakes before a simulator runs.",
    "formula": "1 mm × 1 m² = 1 L; 1 kW × 1 h = 1 kWh",
    "example": "Rain depth of 10 mm over 80 m² with 80% runoff gives 10 × 80 × 0.8 = 640 L. A 2 kW device operating for 3 h uses 6 kWh.",
    "sections": [
      {
        "heading": "Distinguish rate from amount",
        "text": "Watts measure power, a rate of energy transfer, while watt-hours measure an accumulated energy quantity. Liters measure volume; liters per day measure a rate. Multiplying a constant rate by a duration yields an amount under that assumed time profile.",
        "thought": "Why can't you compare 2 kW directly with an 8 kWh battery?"
      },
      {
        "heading": "Why rainwater conversions are simple",
        "text": "A millimeter of rain is a depth of 0.001 meter. Over a square meter it occupies 0.001 cubic meter, which equals one liter. This is geometry, not an empirical rule. Captured volume also depends on the declared collection fraction.",
        "thought": "Compute capture for 5 mm over 20 square meters with 50% runoff."
      },
      {
        "heading": "Keep an explicit time step",
        "text": "A solar model with 1-hour steps converts average kilowatts to kilowatt-hours by multiplying by one hour. If the time step changes to 15 minutes, the energy changes by a factor of four for the same power. Ignoring this creates artificial energy.",
        "thought": "What happens when someone doubles the number of steps but forgets to halve the step duration?"
      },
      {
        "heading": "Know what percentages refer to",
        "text": "Round-trip efficiency, battery state of charge, fraction of demand served and fraction of rain captured are different ratios. Each requires a stated numerator and denominator. A percentage cannot explain itself.",
        "thought": "Which denominator does '90% service' use: demand or generation?"
      }
    ],
    "misconception": "The same numeral with different units is not the same physical quantity.",
    "check": {
      "question": "Which expression estimates energy delivered by a steady 3 kW source during two hours?",
      "choices": [
        "1.5 kWh",
        "6 kW",
        "6 kWh"
      ],
      "answer": 2,
      "explanation": "Energy equals average power multiplied by duration: 3 kW × 2 h = 6 kWh."
    },
    "links": [
      "conservation",
      "water",
      "solar"
    ],
    "lab": "/explore/microgrid/",
    "source": "https://github.com/Rhodan-lab/principle-to-system/blob/main/foundations/03-mathematical-models/overview.md"
  },
  {
    "id": "stocks",
    "domain": "Foundations",
    "title": "Stocks, flows and memory",
    "question": "Why can two identical inputs produce different outcomes?",
    "lead": "A stock remembers the past. A tank, queue or battery can respond differently to identical new inputs because it starts from a different state.",
    "formula": "S(t + Δt) = S(t) + inflow·Δt − outflow·Δt",
    "example": "Two tanks each receive 200 L today. A tank starting empty and one starting nearly full cannot have the same overflow under an identical capacity limit.",
    "sections": [
      {
        "heading": "Stocks integrate history",
        "text": "A state variable stores the consequences of earlier flows. Water stored yesterday can serve demand today; requests left queued yesterday delay today's work. The current value often matters more than the latest input alone.",
        "thought": "Predict how an initially full reservoir responds to sudden rain."
      },
      {
        "heading": "Capacity changes the balance",
        "text": "Physical and computational stores have finite limits. Excess incoming volume may overflow; excess requests may be rejected; excess PV power may be curtailed if storage is full. These are different mechanisms but share a finite-capacity structure.",
        "thought": "Name an alternative to increasing capacity."
      },
      {
        "heading": "Initial conditions are part of the model",
        "text": "A battery at 50% charge is not equivalent to the same battery at 10%. Simulations that omit their initial state may yield plausible but misleading output. Ask for both the initial value and the timing of transfers.",
        "thought": "What changes in a drought model if the reservoir begins full?"
      },
      {
        "heading": "Separate a stock from its indicator",
        "text": "State of charge is a fraction, not stored energy in kWh. A queue length is a count, not a waiting time. A chart of a stock does not directly show the flow rates that produced it, so inspect both.",
        "thought": "Can a high queue length coexist with a low incoming rate?"
      }
    ],
    "misconception": "A stock cannot exceed its declared capacity in a correctly constrained model.",
    "check": {
      "question": "The rain has stopped, but a tank still serves plants. Which model property explains this?",
      "choices": [
        "Stored water carries over from earlier events",
        "Rain is still entering invisibly",
        "Demand creates new water"
      ],
      "answer": 0,
      "explanation": "The tank stores water. Its state records the net effect of earlier capture, use and overflow."
    },
    "links": [
      "conservation",
      "capacity",
      "water"
    ],
    "lab": "/explore/rainwater/",
    "source": "https://github.com/Rhodan-lab/principle-to-system/blob/main/concepts/systems-and-models.md"
  },
  {
    "id": "models",
    "domain": "Mathematics",
    "title": "A model is a conditional claim",
    "question": "What does a simulation actually prove?",
    "lead": "Every model replaces the world with a selected set of relationships. Its output is a consequence of assumptions and inputs, not automatic proof of reality.",
    "formula": "Model + inputs + assumptions → conditional prediction",
    "example": "A microgrid's 12-hour energy balance can check whether simulated energy meets a load. It cannot certify inverter controls, protection coordination or safe islanding.",
    "sections": [
      {
        "heading": "Models encode purposeful simplification",
        "text": "A good model does not contain everything; it retains what is needed for the question. A fluid queue can illuminate overload without representing every random arrival. A solar area formula can estimate energy while ignoring individual circuit behavior.",
        "thought": "What question can a simple model answer well?"
      },
      {
        "heading": "Verification and validation differ",
        "text": "Verification asks whether the implementation solves the stated equations correctly. Validation asks how well the model represents observed reality for its intended use. A simulator can be verified against an exact solution and still be unsuitable for a different physical appliance.",
        "thought": "Is passing unit tests evidence of installation safety?"
      },
      {
        "heading": "Parameters have interpretation",
        "text": "A capacity may be treated as fixed for a scenario even though real capacity degrades. A one-pass retry fraction can illuminate extra demand without modeling recursive retries. Explicit parameter meaning prevents accidental overgeneralization.",
        "thought": "Which simplification would be unsafe to forget in a service outage?"
      },
      {
        "heading": "Evidence changes the model",
        "text": "Measurements, alternative models and failure cases should challenge the original assumptions. A reliable learning process asks where predictions deviate, which parameter matters and what new data would discriminate between explanations.",
        "thought": "What would falsify a simple uniform-solar-output assumption?"
      }
    ],
    "misconception": "A highly precise output is not necessarily an accurate representation of the world.",
    "check": {
      "question": "A program conserves energy in every internal test. What can you conclude?",
      "choices": [
        "The scenario will happen exactly in real weather",
        "Its implementation matches its stated accounting rules",
        "The hardware is electrically safe"
      ],
      "answer": 1,
      "explanation": "Conservation tests support implementation verification, not external validation or hardware certification."
    },
    "links": [
      "uncertainty",
      "causality",
      "evidence"
    ],
    "lab": "/explore/microgrid/",
    "source": "https://github.com/Rhodan-lab/principle-to-system/blob/main/concepts/systems-and-models.md"
  },
  {
    "id": "feedback",
    "domain": "Systems",
    "title": "Feedback changes the future",
    "question": "When does a response amplify the very problem it tries to solve?",
    "lead": "Feedback occurs when a system's output changes the conditions of its future input. Delays, saturation and blind spots determine whether correction becomes control or escalation.",
    "formula": "state → observation → decision → action → new state",
    "example": "A timed retry adds work precisely when a struggling service already has too much. Without a limit or backoff, the response can reinforce overload.",
    "sections": [
      {
        "heading": "Corrective and reinforcing loops",
        "text": "Negative feedback acts to oppose a deviation from a target; positive feedback reinforces a change. These labels describe loop structure, not whether an effect is desirable or harmful. A controller that turns cooling on when temperature rises provides a corrective loop.",
        "thought": "Where is the sensor in a thermostat loop?"
      },
      {
        "heading": "Delays matter",
        "text": "A response calculated from old information can overshoot. A tank's level measurement can lag a fast storm; a retry strategy may react before the original request has actually failed. Communication, sampling and action delays must be included for realistic control design.",
        "thought": "How can an old measurement cause a wrong command?"
      },
      {
        "heading": "Capacity and saturation",
        "text": "Even a sensible corrective controller cannot produce power or service capacity that the hardware lacks. Once an actuator saturates, stronger commands cannot guarantee stronger action. Feedback should be analyzed with its resource constraints.",
        "thought": "Can a full battery absorb any more solar energy?"
      },
      {
        "heading": "A loop must be tested over time",
        "text": "A diagram identifies the loop, but the trajectory may require dynamics, time constants and disturbances. Stable-looking behavior in one scenario need not survive a longer delay or larger perturbation.",
        "thought": "Which input would you vary to test a retry feedback loop?"
      }
    ],
    "misconception": "Positive feedback does not mean 'good feedback'; it means a change reinforces itself.",
    "check": {
      "question": "Why can immediate automatic retries make an overloaded service worse?",
      "choices": [
        "Retries increase server capacity automatically",
        "The queue stores unlimited requests",
        "Retries raise the offered work the service must process"
      ],
      "answer": 2,
      "explanation": "A retry is another request. It raises offered load while service capacity may be unchanged."
    },
    "links": [
      "queue",
      "capacity",
      "resilience"
    ],
    "lab": "/learn/distributed-information/",
    "source": "https://github.com/Rhodan-lab/principle-to-system/blob/main/technology/20-sensors-control-infrastructure/overview.md"
  },
  {
    "id": "capacity",
    "domain": "Systems",
    "title": "Thresholds and bottlenecks",
    "question": "What changes when demand outruns service?",
    "lead": "A capacity limit often creates a qualitative change. Below a threshold a system may keep up; above it, a backlog grows until another limit forces rejection or failure.",
    "formula": "Net accumulation rate = incoming rate − service rate",
    "example": "If 11 requests arrive each second and 10 complete each second, a fluid-model queue gains roughly one request per second until its finite capacity is reached.",
    "sections": [
      {
        "heading": "Separate demand from service",
        "text": "A server's incoming request rate and processing capacity are rates; its queue is a stock. A water tank has storage capacity and outlet demand; a microgrid has energy capacity and instantaneous power constraints. Similar words conceal different dimensions.",
        "thought": "Which quantity caps the request queue: requests or requests per second?"
      },
      {
        "heading": "Below and above the threshold",
        "text": "When a constant arrival rate is below a constant service rate, an initially empty ideal fluid queue stays empty. Above capacity, it accumulates at their difference until the buffer fills. More arriving work is then rejected in this approximation.",
        "thought": "At what net rate does a queue grow when arrivals are 13/s and service 10/s?"
      },
      {
        "heading": "Real systems are less smooth",
        "text": "Bursty arrivals can overload a service even if the long-run average is below capacity. Latency, scheduling, failure, adaptive retries and resource sharing require more detailed models. A simple fluid simulation is a lens, not a production traffic simulator.",
        "thought": "Why is a daily average insufficient for peak demand planning?"
      },
      {
        "heading": "Bottlenecks move",
        "text": "Increasing one capacity may expose another. A larger battery helps with energy shortages but not necessarily inverter power limits; a bigger queue delays rejection but can increase latency. A good redesign asks what outcome matters, not simply what number can grow.",
        "thought": "What is the downside of making a queue arbitrarily large?"
      }
    ],
    "misconception": "Buffer capacity (items) and service capacity (items per second) are different.",
    "check": {
      "question": "Arrivals are 13 requests/s and service is 10 requests/s. Before the queue fills, what happens?",
      "choices": [
        "Backlog grows by about 3 requests/s",
        "Backlog shrinks by 3 requests/s",
        "The service rate rises automatically"
      ],
      "answer": 0,
      "explanation": "The constant-rate fluid model accumulates the excess offered work: 13 − 10 = 3 requests each second."
    },
    "links": [
      "queue",
      "feedback",
      "stocks"
    ],
    "lab": "/learn/distributed-information/",
    "source": "https://github.com/Rhodan-lab/principle-to-system/blob/main/foundations/03-mathematical-models/overview.md"
  },
  {
    "id": "heat",
    "domain": "Energy",
    "title": "Heat flows; refrigerators pump it",
    "question": "Why does cooling one place warm another?",
    "lead": "A refrigerator does not manufacture cold. It uses work to transport thermal energy across a temperature difference.",
    "formula": "C·dT/dt = UA(Troom − T) + Pload − Pcool",
    "example": "At 28°C room and 8°C cabinet, UA=3.2 W/K gives 64 W entering through the walls. Add 18 W internal load and subtract 95 W cooling: the initial cabinet balance is −13 W.",
    "sections": [
      {
        "heading": "Conduction drives the leak",
        "text": "When the room is warmer than the cabinet, heat flows inward through its boundaries. A lumped conductance UA in W/K multiplies the temperature difference to approximate watts of heat transfer. It is a simplified boundary property, not a universal constant.",
        "thought": "If the room warms further, what happens to the inward heat leak?"
      },
      {
        "heading": "Active cooling is a power term",
        "text": "In the cabinet energy balance, cooling appears as a subtraction because it removes energy. At the room boundary, the appliance rejects captured heat plus electrical work consumed (ignoring distribution details). These perspectives are consistent because their boundaries differ.",
        "thought": "Where does electrical work end up after running the compressor?"
      },
      {
        "heading": "State changes over time",
        "text": "Thermal capacitance C in J/K measures how much energy changes cabinet temperature. A net −13 W tends to lower temperature, but not instantly. As the cabinet cools, the inward heat leak increases and the net rate approaches equilibrium under fixed assumptions.",
        "thought": "Why is the initial power balance not the final temperature?"
      },
      {
        "heading": "What the lab cannot decide",
        "text": "The model neglects compressor cycling details, door openings, temperature stratification and the full room's air balance. Its equilibrium temperature can check a numerical solver but cannot be treated as a real appliance measurement.",
        "thought": "Which real-world event would invalidate constant room temperature?"
      }
    ],
    "misconception": "Cooling power and electrical input power are not interchangeable without a coefficient-of-performance model.",
    "check": {
      "question": "With 64 W entering through walls and 18 W internal load, what does 95 W of active cooling initially do?",
      "choices": [
        "Forces an immediate 13°C temperature drop",
        "Produces a net 13 W removal from the cabinet",
        "Creates 95 W of energy"
      ],
      "answer": 1,
      "explanation": "64 + 18 − 95 = −13 W. The sign indicates energy leaves the cabinet initially; it is not a temperature change."
    },
    "links": [
      "conservation",
      "systems",
      "models"
    ],
    "lab": "/learn/refrigerator/",
    "source": "https://github.com/Rhodan-lab/principle-to-system/blob/main/science/08-energy-thermodynamics/overview.md"
  },
  {
    "id": "queue",
    "domain": "Computation",
    "title": "When retries become a second flood",
    "question": "Why can a reasonable response cascade into overload?",
    "lead": "Retries are not free. If an external request creates another attempt, a struggling service receives more work than users originally sent.",
    "formula": "λoffered = λexternal × (1 + pretry); ρ = λoffered / μ",
    "example": "7.5 external requests/s with a one-pass 50% retry fraction gives 11.25 requests/s offered. Against service capacity 10/s, the modeled queue accumulates 1.25 requests/s until its bounded buffer fills.",
    "sections": [
      {
        "heading": "Separate external and offered load",
        "text": "External arrivals are user-initiated. Offered load counts the additional attempts created by the chosen retry rule. A one-pass retry fraction does not model recursive, repeated retries or correlated timeouts; those require different assumptions.",
        "thought": "What is added when p_retry grows but external arrival rate stays fixed?"
      },
      {
        "heading": "A bounded fluid approximation",
        "text": "The simple learner model treats rates as steady and a queue as a continuous quantity. While offered work exceeds service and the buffer has space, backlog grows at their difference. Once full, excess new work is rejected in this approximation.",
        "thought": "Why can a bigger queue postpone rejection without solving overload?"
      },
      {
        "heading": "Mean delay is a separate model",
        "text": "A stationary M/M/1 approximation can illustrate expected time when arrivals are random, service times exponential and utilization remains below one. Its mean delay is not the deterministic finite-buffer fluid backlog and is not defined as a stable stationary mean above service capacity.",
        "thought": "Should an overloaded deterministic queue display a valid stationary M/M/1 delay?"
      },
      {
        "heading": "Better systems use more than retries",
        "text": "Backoff, jitter, timeouts, caching, admission control, shed load and capacity management can reduce pressure, but each has consequences. The appropriate trade-off depends on service objectives and the actual request process.",
        "thought": "Which safeguard reduces incoming work before it reaches the queue?"
      }
    ],
    "misconception": "The formula with one additional attempt is not a recursive retry-storm law.",
    "check": {
      "question": "At 7.5 external requests/s with 50% one-pass retries, what is the offered rate?",
      "choices": [
        "7.5 requests/s",
        "15 requests/s",
        "11.25 requests/s"
      ],
      "answer": 2,
      "explanation": "Multiply 7.5 by 1 + 0.5 to count the original arrivals and the additional attempts."
    },
    "links": [
      "feedback",
      "capacity",
      "resilience"
    ],
    "lab": "/learn/distributed-information/",
    "source": "https://github.com/Rhodan-lab/principle-to-system/blob/main/software/product_alpha/routes/distributed-information.json"
  },
  {
    "id": "water",
    "domain": "Earth & Water",
    "title": "The time structure of rainfall",
    "question": "Why doesn't yearly rainfall guarantee daily water supply?",
    "lead": "Even abundant rain may arrive at the wrong time. A finite tank can overflow in storms and run dry between them.",
    "formula": "Vcapture (L) = rainfall (mm) × area (m²) × runoff fraction",
    "example": "A 10 mm event on 80 m² with 80% capture yields 640 liters. If demand takes 90 liters that day, an initially empty 800-liter tank ends with 550 liters, before any unmodeled losses.",
    "sections": [
      {
        "heading": "Rain arrives in events",
        "text": "Annual totals hide the difference between gentle regular rain and extreme isolated storms. Storage is constrained by the order of events and daily demand. The same total can produce very different overflow and service coverage.",
        "thought": "How could two cities with equal annual rainfall need different storage?"
      },
      {
        "heading": "Convert depth into volume",
        "text": "One millimeter of water on one square meter is exactly one liter. The catchment area and dimensionless runoff factor determine a simplified captured volume. Real conveyance and first-flush losses may reduce that amount.",
        "thought": "What happens if the catchment surface absorbs more rainfall?"
      },
      {
        "heading": "A finite tank cannot save all storms",
        "text": "Demand reduces stored water; when capture exceeds remaining capacity, overflow leaves the modeled tank. Increasing capacity can help during some dry spells, but it cannot guarantee safety or perfect coverage across all possible weather sequences.",
        "thought": "Does eliminating overflow require an infinitely large tank?"
      },
      {
        "heading": "Water use and safety are separate",
        "text": "A volume ledger does not measure pathogens, chemicals, roof contamination, stagnant conditions, mosquito control, structural loads, or plumbing protection. This educational model is exclusively conceptual and non-potable; no drinking-water claims follow.",
        "thought": "What evidence would be required before any real installation?"
      }
    ],
    "misconception": "High rainwater capture does not imply water is clean or safe to drink.",
    "check": {
      "question": "A storm brings more water than the tank can hold, even after daily use. Where does the excess go?",
      "choices": [
        "Modeled overflow",
        "It disappears without a term",
        "It becomes potable water"
      ],
      "answer": 0,
      "explanation": "Overflow is the positive remainder after use and the tank's finite remaining capacity have been accounted for."
    },
    "links": [
      "conservation",
      "stocks",
      "units"
    ],
    "lab": "/explore/rainwater/",
    "source": "https://github.com/Rhodan-lab/principle-to-system/blob/main/design-challenges/nonpotable-rainwater-buffer.md"
  },
  {
    "id": "solar",
    "domain": "Energy",
    "title": "Sunlight, batteries and demand",
    "question": "What has to balance during an outage?",
    "lead": "A solar–battery system coordinates changing generation and a finite reserve. Being energy-positive over a day is not the same as serving every hour.",
    "formula": "Ppv = G × A × η; Enew = Eold + ηc·Echarge − Edelivered/ηd",
    "example": "800 W/m² across 16 m² of panel area at 18% conversion yields 2.304 kW. Over a one-hour constant-input step this corresponds to 2.304 kWh before other system losses.",
    "sections": [
      {
        "heading": "From sunlight to electrical power",
        "text": "A simplified PV power estimate multiplies irradiance, active area and operating efficiency. The result is a rate; multiply by hours to obtain energy. Temperature, shading pattern, mismatch, inverters and degradation can change real production.",
        "thought": "If irradiance halves under the simple model, what happens to PV power?"
      },
      {
        "heading": "Battery energy has two directions",
        "text": "Charging raises the stored state but loses some energy; discharging delivers less to loads than is removed from the battery. Reserve constraints restrict how far the state may fall. Charge and discharge efficiencies need not be equal in real equipment.",
        "thought": "Why does a battery deliver less energy than is removed from storage?"
      },
      {
        "heading": "Reliability is about time",
        "text": "A twelve-hour energy total can look sufficient while one dark hour lacks enough battery energy to serve its critical load. The meaningful service metric is unserved critical energy under the stated hourly scenario.",
        "thought": "What could improve service during a cloudy afternoon besides bigger panels?"
      },
      {
        "heading": "Electrical reality is more complex",
        "text": "Grid-forming operation, grounding, protection, temperature, inverter power limits and reconnection behavior are not covered by a simple energy ledger. A favorable synthetic result is not an installation plan or safety approval.",
        "thought": "Which omitted variable matters during sudden power surges?"
      }
    ],
    "misconception": "Battery capacity in kWh does not specify how many kilowatts the inverter can supply at once.",
    "check": {
      "question": "What does 2 kW of output sustained for one hour deliver?",
      "choices": [
        "0.5 kWh",
        "2 kWh",
        "2 kW/h"
      ],
      "answer": 1,
      "explanation": "Energy is power integrated through time: 2 kW × 1 h = 2 kWh."
    },
    "links": [
      "units",
      "resilience",
      "conservation"
    ],
    "lab": "/explore/microgrid/",
    "source": "https://github.com/Rhodan-lab/principle-to-system/blob/main/system-dossiers/solar-battery-microgrid.md"
  },
  {
    "id": "uncertainty",
    "domain": "Reasoning",
    "title": "Uncertainty is part of knowledge",
    "question": "How confident is this result—and why?",
    "lead": "A precise number may conceal assumptions, uncertain inputs, noisy measurements and an inadequate model. Scientific explanation separates each source of uncertainty.",
    "formula": "Observation − prediction = residual",
    "example": "If a sensor reports 20.4°C and a model predicts 20.0°C, the residual is +0.4°C under that sign convention. It does not by itself say which assumption is wrong.",
    "sections": [
      {
        "heading": "Four useful distinctions",
        "text": "Measurement uncertainty concerns observed quantities; parameter uncertainty concerns model inputs; structural uncertainty concerns whether important mechanisms are missing; scenario uncertainty concerns future forcing such as weather or traffic.",
        "thought": "Which uncertainty grows when the solar forecast changes?"
      },
      {
        "heading": "Sensitivity asks what matters",
        "text": "Vary one parameter across a plausible range to see how the output responds under the chosen model. A sharp transition near a limit is often worth studying. Sensitivity is not proof of causal importance in the actual world.",
        "thought": "Which variable should you vary to examine overload risk?"
      },
      {
        "heading": "Errors can be systematic",
        "text": "A sensor may drift, a boundary may omit leakage, a model may consistently ignore shading. Averaging more readings does not remove every bias. Compare independent evidence and ask what observation could reveal the omission.",
        "thought": "Does measuring the wrong variable more precisely solve the problem?"
      },
      {
        "heading": "Report the envelope, not only the answer",
        "text": "Good explanations say what was varied, the range of scenarios, time period, units and consequences of violated assumptions. A synthetic eight-day rainfall result should never be described as a local climate forecast.",
        "thought": "Which phrase distinguishes a simulated outcome from a prediction of actual weather?"
      }
    ],
    "misconception": "An extra decimal place does not mean an extra decimal place of justified confidence.",
    "check": {
      "question": "What does a numerical model passing its own conservation check establish?",
      "choices": [
        "All important real-world effects were included",
        "There is no uncertainty",
        "Its internal accounting is consistent"
      ],
      "answer": 2,
      "explanation": "Internal consistency is useful verification, but physical validity and uncertain conditions require independent evidence."
    },
    "links": [
      "models",
      "evidence",
      "causality"
    ],
    "lab": "/explore/",
    "source": "https://github.com/Rhodan-lab/principle-to-system/blob/main/foundations/02-measurement-uncertainty/overview.md"
  },
  {
    "id": "causality",
    "domain": "Reasoning",
    "title": "Correlation is not a mechanism",
    "question": "How do you know what made the result change?",
    "lead": "A model can show what follows from its own assumptions, while an observation can show what happened. Neither alone identifies every real-world cause.",
    "formula": "Cause hypothesis → mechanism → predicted observation → discriminating test",
    "example": "A solar array loses output while a cloud passes. Clouds are a hypothesis, but temperature, curtailment, inverter behavior or shading could also change output.",
    "sections": [
      {
        "heading": "Separate pattern and explanation",
        "text": "Two quantities can move together because one affects the other, because both respond to a third variable, or by coincidence. A convincing explanation names the mechanism and predicts what changes if the cause is altered.",
        "thought": "What else might explain lower PV output at noon?"
      },
      {
        "heading": "Interventions help",
        "text": "Within a mathematical simulation you can vary one input while holding the others fixed, producing a clean conditional comparison. In a field study, inputs often co-vary; experiments, careful measurement and design are needed to separate effects.",
        "thought": "What does 'all else equal' mean in a model?"
      },
      {
        "heading": "Look for competing hypotheses",
        "text": "If water disappears from a tank, leakage, evaporation, uncounted demand or sensor error are all candidates. A strong test should produce different predicted observations under competing explanations.",
        "thought": "What observation would distinguish a leak from increased demand?"
      },
      {
        "heading": "Avoid overstating a counterfactual",
        "text": "Saying the model serves 10% more demand with added storage means 'within this model and scenario'. Real installation outcomes depend on constraints, weather and behavior not represented in the experiment.",
        "thought": "How would you word the result without claiming field validation?"
      }
    ],
    "misconception": "An apparently realistic animation is not empirical evidence for the mechanism it depicts.",
    "check": {
      "question": "A simulated tank improves coverage after increasing capacity. What does that demonstrate?",
      "choices": [
        "A conditional relationship within the model",
        "That real tanks are guaranteed to save the same amount",
        "That rainfall patterns never matter"
      ],
      "answer": 0,
      "explanation": "The simulation isolates an input under its own assumptions, not all real-world confounders."
    },
    "links": [
      "models",
      "uncertainty",
      "evidence"
    ],
    "lab": "/explore/rainwater/",
    "source": "https://github.com/Rhodan-lab/principle-to-system/blob/main/foundations/01-scientific-reasoning/overview.md"
  },
  {
    "id": "resilience",
    "domain": "Systems",
    "title": "Efficiency is not resilience",
    "question": "What is the system optimized to survive?",
    "lead": "Systems optimized for average efficiency may underperform during unusual but consequential disruptions. Resilience begins by defining the essential service and stress scenarios.",
    "formula": "Unserved energy = Σ max(0, critical demand − served) × Δt",
    "example": "A low-energy-use server or microgrid may perform well on average but lack margin when demand spikes or sunlight falls. A reserve can reduce immediate efficiency while preserving future service.",
    "sections": [
      {
        "heading": "Define service first",
        "text": "Is the goal keeping a refrigerator under a temperature limit, serving requests within a deadline, or keeping hospital loads supplied? Without a target, 'reliable' and 'efficient' are ambiguous. Choose the service boundary, horizon and acceptable failure before choosing a metric.",
        "thought": "What failure matters most in a critical-load microgrid?"
      },
      {
        "heading": "Reserve trades present output for future options",
        "text": "A battery kept above a fixed reserve cannot deliver that reserved energy during the current modeled period. This can reduce current service while preserving future options; whether that is beneficial requires the particular policy and scenario.",
        "thought": "What happens if the model allows draining the entire battery?"
      },
      {
        "heading": "Failure may cascade across components",
        "text": "A service retry can intensify overload; a faulty sensor may trigger the wrong controller response; the same upstream power supply can defeat apparently independent redundant equipment. Resilience analysis should examine dependencies, not only component ratings.",
        "thought": "Find a common dependency shared by two 'backup' devices."
      },
      {
        "heading": "Scenario tests are not guarantees",
        "text": "Test dry periods, storms, shade, surges, and control delays. Report the unmet service for each scenario and the omitted failure modes. Performance in one favorable simulation is not a certification of broader resilience.",
        "thought": "Which stress case exposes a fragile reserve policy?"
      }
    ],
    "misconception": "Maximum average utilization can coexist with poor resilience to spikes.",
    "check": {
      "question": "Which metric directly expresses loss of critical electricity service?",
      "choices": [
        "Battery purchase price",
        "Unserved critical energy (kWh)",
        "Total PV nameplate power (kW)"
      ],
      "answer": 1,
      "explanation": "Unserved critical energy accumulates the gap between required and supplied service over time."
    },
    "links": [
      "capacity",
      "solar",
      "feedback"
    ],
    "lab": "/explore/microgrid/",
    "source": "https://github.com/Rhodan-lab/principle-to-system/blob/main/system-dossiers/solar-battery-microgrid.md"
  },
  {
    "id": "evidence",
    "domain": "Reasoning",
    "title": "A source is not a verdict",
    "question": "When does an evidence link justify confidence?",
    "lead": "A linked claim, a version identifier and a reviewed record each answer different questions. Provenance helps you inspect an assertion but does not itself make the assertion true.",
    "formula": "Source identity ≠ review decision ≠ truth",
    "example": "A precise Atlas revision can establish which record you examined. Whether its claim is adequately supported requires inspecting reasoning, sources, limitations, conflicting evidence and the relevant human decision.",
    "sections": [
      {
        "heading": "Start with identity",
        "text": "Identify the precise artifact, version and scope. An exact revision lets different readers inspect the same material instead of silently reading a later edit. Identity is a prerequisite for auditing, not a measure of scientific correctness.",
        "thought": "Would two different revisions count as the same evidence object?"
      },
      {
        "heading": "Trace the claim to its support",
        "text": "Ask which observed facts or sources support the assertion and which assumptions connect them. A polished explanation with no trail may be persuasive but not inspectable. Missing evidence should remain visibly missing.",
        "thought": "What would you request when a source reference is unavailable?"
      },
      {
        "heading": "Keep reviews separate",
        "text": "Principia learning models and Atlas research records have different authorities. Linking one to the other must not promote a simulation to a human-verified scientific claim or alter a canonical review state.",
        "thought": "Can a homepage style badge approve a claim?"
      },
      {
        "heading": "Maintain room for correction",
        "text": "A useful research workspace shows unresolved questions and limitations as first-class content, not inconvenient footnotes. Confidence should change when new evidence arrives, but accepted source decisions require their own authorized process.",
        "thought": "What would convince you to revise a conclusion?"
      }
    ],
    "misconception": "A pinned export is not a live, continually updated or independently verified knowledge database.",
    "check": {
      "question": "What does the exact commit of a research export establish?",
      "choices": [
        "That every contained claim is true",
        "That a human has approved all future changes",
        "Which source revision was packaged"
      ],
      "answer": 2,
      "explanation": "The commit fixes artifact identity. Evidence evaluation and human authority remain separate processes."
    },
    "links": [
      "models",
      "uncertainty",
      "systems"
    ],
    "lab": "/research/",
    "source": "https://github.com/Rhodan-lab/principle-to-system/blob/main/concepts/systems-and-models.md"
  }
];
const byId=Object.fromEntries(topics.map(topic=>[topic.id,topic]));
const domains=[...new Set(topics.map(t=>t.domain))];
const normalize=s=>String(s??"").normalize("NFKD").toLowerCase().trim().replace(/\s+/g," ");
function search(query,domain="All"){const q=normalize(query);return topics.filter(t=>(domain==="All"||t.domain===domain)&&normalize(t.title+" "+t.question+" "+t.lead+" "+t.domain+" "+t.sections.map(s=>s.heading).join(" ")).includes(q))}
function resolve(id){return Object.hasOwn(byId,id)?byId[id]:null}
function linkTo(id){return "/knowledge/#"+encodeURIComponent(id)}
function checkAnswer(id,answer){const t=resolve(id);if(!t)throw new RangeError("Unknown knowledge topic");if(!Number.isInteger(answer)||answer<0||answer>=t.check.choices.length)throw new RangeError("Invalid answer index");return {correct:answer===t.check.answer,explanation:t.check.explanation,expected:t.check.answer}}
return {topics,byId,domains,normalize,search,resolve,linkTo,checkAnswer};
});
