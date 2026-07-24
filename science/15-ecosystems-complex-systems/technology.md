---
title: "Engineering with Ecosystems: Bioremediation and Closed Ecological Systems"
slug: "15-ecosystems-complex-systems-tech"
module: "Module 15: Ecosystems, feedback, networks, and complex systems"
domain: "technology"
status: draft
prerequisites: ["15-ecosystems-complex-systems"]
connections: ["18-agricultural-engineering", "22-environmental-control-systems"]
last_reviewed: 2026-07-24
content_license: CC-BY-4.0
---

# Engineering with Ecosystems: Bioremediation and Closed Ecological Systems

## 1. Scientific principles used

The engineering of ecological systems relies on the principles of biogeochemical cycling, trophic dynamics, and network resilience. By understanding how matter (such as carbon, nitrogen, and phosphorus) flows through food webs and is transformed by microbial metabolism, engineers can design systems that harness these natural processes. The principle of competitive exclusion is used to manage microbial populations, while the concept of carrying capacity dictates the sizing and loading rates of biological reactors. Furthermore, the principles of self-organisation and feedback loops are leveraged to create systems that can autonomously adjust to varying inputs and maintain stability without constant human intervention.

## 2. The engineering problem

Human activities generate vast quantities of organic waste, toxic pollutants, and excess nutrients that overwhelm natural ecosystems, leading to eutrophication and habitat destruction. The engineering problem is twofold: first, how to design controlled environments (such as wastewater treatment plants or constructed wetlands) that accelerate the natural degradation of these pollutants; and second, how to design entirely closed ecological life support systems (CELSS) for space exploration, where every atom of carbon, oxygen, and water must be continuously recycled to sustain human life indefinitely.

## 3. Main components

A typical engineered ecosystem, such as a constructed wetland for wastewater treatment, consists of several key components:
- **Substrate:** A porous medium (gravel, sand, or soil) that provides physical support for plants and a vast surface area for microbial biofilms.
- **Macrophytes:** Aquatic plants (e.g., reeds, bulrushes) that oxygenate the substrate through their roots, take up nutrients, and provide a microhabitat for microbes.
- **Microbial Consortia:** The "engine" of the system, comprising diverse bacteria and archaea that perform aerobic and anaerobic digestion, nitrification, and denitrification.
- **Hydraulic Control Structures:** Pumps, weirs, and piping that regulate the flow rate, retention time, and water level, ensuring optimal contact between the pollutants and the biological components.

## 4. How the components interact

The interaction between components is highly synergistic. Wastewater enters the substrate, where physical filtration traps suspended solids. The macrophytes transport oxygen from the atmosphere down into their root zones (rhizospheres), creating oxygen-rich micro-zones within an otherwise anaerobic substrate. This spatial heterogeneity allows aerobic bacteria to oxidise ammonia into nitrate (nitrification) near the roots, while anaerobic bacteria in the surrounding substrate reduce the nitrate into nitrogen gas (denitrification), which escapes into the atmosphere. The plants also absorb some nutrients directly, while their root exudates provide carbon sources that fuel microbial metabolism.

## 5. Matter, energy, force, or information flow

**Matter Flow:** The system is fundamentally a matter-transformation engine. Complex organic molecules (measured as Biological Oxygen Demand, or BOD) are broken down into simpler compounds ($CO_2$, $H_2O$, $CH_4$). Nitrogen compounds are cycled from ammonia to nitrate to nitrogen gas. Phosphorus is largely removed through chemical precipitation and adsorption onto the substrate.

**Energy Flow:** In constructed wetlands, the primary energy input is solar radiation, which drives plant photosynthesis and evapotranspiration. The chemical energy stored in the wastewater's organic bonds is released by microbial respiration, generating heat. In intensive bioreactors (like activated sludge systems), significant electrical energy is required to mechanically aerate the water and pump the sludge.

**Information Flow:** Information in these systems is primarily chemical. Microbes communicate via quorum sensing (releasing signalling molecules to coordinate gene expression based on population density). Engineers monitor the system by measuring chemical parameters (pH, dissolved oxygen, oxidation-reduction potential) and use this information to adjust hydraulic flows, creating a cybernetic feedback loop.

## 6. System architecture

Engineered ecosystems can be classified by their architectural openness:
- **Open Systems:** Constructed wetlands and agricultural buffers. They are open to the atmosphere and local hydrology, relying on solar energy and natural ecological succession. They are robust but require large land areas.
- **Semi-Closed Systems:** Activated sludge wastewater treatment plants. They control the flow of water and the concentration of microbes (by recycling sludge), but are open to the atmosphere. They are compact and fast but energy-intensive.
- **Closed Systems:** Closed Ecological Life Support Systems (CELSS), such as the Biosphere 2 experiment or the Micro-Ecological Life Support System Alternative (MELiSSA) developed by the European Space Agency. These are hermetically sealed architectures where all matter must be recycled. MELiSSA uses a highly modular architecture with separate, tightly controlled bioreactors for waste degradation, nitrification, and photosynthetic oxygen/food production, connected by precise fluidic loops.

## 7. Design constraints

- **Hydraulic Retention Time (HRT):** The fluid must remain in the system long enough for slow-growing microbes (like nitrifying bacteria) to perform their metabolic functions.
- **Stoichiometric Balance:** In closed systems, the ratio of elements (Carbon:Nitrogen:Phosphorus) must be strictly maintained. If a crop absorbs too much nitrogen relative to carbon, the downstream microbial digesters will stall.
- **Toxicity Thresholds:** While microbes can degrade many toxins, sudden spikes in heavy metals or industrial chemicals can poison the biofilm, causing a catastrophic system failure.

## 8. Performance and efficiency

Performance is typically measured by the removal efficiency of specific pollutants. A well-designed constructed wetland can achieve >90% removal of BOD and suspended solids, and 70-90% removal of nitrogen. Efficiency is often evaluated in terms of energy consumed per kilogram of pollutant removed. Natural systems like wetlands are highly energy-efficient but have low volumetric efficiency (they require a lot of space). Mechanical systems have high volumetric efficiency but poor energy efficiency.

## 9. Reliability and failure modes

Engineered ecosystems are generally highly reliable due to their internal redundancy; if one microbial species fails, another often fills its niche. However, they are susceptible to specific failure modes:
- **Clogging:** The accumulation of non-degradable solids and excessive microbial biomass can clog the porous substrate, causing surface pooling and short-circuiting of the hydraulic flow.
- **Regime Shifts:** A sudden change in pH or temperature can cause a rapid shift in the microbial community, such as a transition from beneficial floc-forming bacteria to filamentous bacteria, which causes "sludge bulking" and prevents the separation of clean water from the biomass.
- **Atmospheric Imbalance:** In closed systems like Biosphere 2, unexpected sinks (such as concrete absorbing $CO_2$) or overactive soil microbes can rapidly deplete atmospheric oxygen, threatening the survival of the human crew and requiring emergency intervention [1].

## 10. Safety principles

Safety in engineered ecosystems involves preventing the release of pathogens and managing hazardous byproducts. Systems must be designed to prevent the aerosolisation of untreated wastewater. Anaerobic digestion produces biogas (primarily methane), which poses an explosion hazard if not properly vented, captured, or flared. In closed life support systems, the primary safety principle is strict compartmentalisation and the inclusion of physicochemical backup systems (like chemical $CO_2$ scrubbers) to prevent lethal atmospheric imbalances.

## 11. Environmental and lifecycle considerations

Constructed wetlands offer significant secondary environmental benefits, including habitat creation for wildlife, carbon sequestration, and aesthetic value. Their lifecycle costs are heavily weighted toward initial land acquisition and earthworks, with very low operational and maintenance costs compared to mechanical treatment plants. At the end of their lifecycle, the substrate may need to be excavated and treated as hazardous waste if it has accumulated high levels of heavy metals.

## 12. Connections to other technologies

- **18-agricultural-engineering:** Aquaponics and precision agriculture utilise similar principles of nutrient cycling and controlled microbial environments.
- **22-environmental-control-systems:** HVAC systems and chemical scrubbers are often integrated with biological systems to provide hybrid life support in aerospace engineering.
- **Synthetic Biology:** The future of engineered ecosystems involves designing synthetic microbial consortia with engineered metabolic pathways to degrade novel plastics or produce specific biofuels.

## 13. Sources

[1] Cohen, J. E., & Tilman, D. (1996). Biosphere 2 and biodiversity: the lessons so far. *Science*, 274(5290), 1150-1151.
[2] Kadlec, R. H., & Wallace, S. (2008). *Treatment Wetlands* (2nd ed.). CRC Press.
[3] Lasseur, C., et al. (2010). MELiSSA: the European project of closed life support system. *Gravitational and Space Research*, 23(2).
[4] Odum, H. T. (1983). *Systems Ecology: An Introduction*. John Wiley & Sons.
