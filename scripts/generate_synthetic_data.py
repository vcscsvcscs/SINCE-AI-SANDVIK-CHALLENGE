#!/usr/bin/env python3
"""
Generate comprehensive synthetic data for Sandvik spare-part agent challenge
"""

import random
import json
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Base part categories and components
PART_CATEGORIES = {
    "ENGINE": ["TURBOCHARGER", "ALTERNATOR", "STARTER", "FUEL PUMP", "INJECTOR", "CRANKSHAFT", "PISTON", "CYLINDER", "MANIFOLD", "VALVE"],
    "HYDRAULICS": ["PUMP", "CYLINDER", "HOSE", "VALVE", "ACCUMULATOR", "MANIFOLD", "FILTER", "RESERVOIR", "COUPLING", "ADAPTER"],
    "TRANSMISSION": ["GEARBOX", "TRANSMISSION", "CONVERTER", "CLUTCH", "DIFFERENTIAL", "GEAR", "DRIVESHAFT", "BEARING", "SEAL", "CARRIER"],
    "ELECTRICAL": ["ALTERNATOR", "BATTERY", "SENSOR", "SWITCH", "RELAY", "FUSE", "CABLE", "CONNECTOR", "DISPLAY", "CONTROLLER"],
    "CABIN": ["SEAT", "JOYSTICK", "MIRROR", "WINDOW", "DOOR", "HANDLE", "DASHBOARD", "PANEL", "UPHOLSTERY", "CONSOLE"],
    "COOLING": ["RADIATOR", "FAN", "COOLER", "HOSE", "PUMP", "THERMOSTAT", "CONDENSER", "EVAPORATOR", "COMPRESSOR", "DRYER"],
    "BRAKE": ["DISC", "PAD", "CYLINDER", "VALVE", "HOSE", "CALIPER", "ACTUATOR", "ACCUMULATOR", "SENSOR", "SWITCH"],
    "STRUCTURAL": ["BRACKET", "PLATE", "BEAM", "FRAME", "GUARD", "COVER", "SHIELD", "PANEL", "SUPPORT", "MOUNT"],
    "FASTENERS": ["BOLT", "NUT", "WASHER", "SCREW", "PIN", "CLIP", "RING", "CLAMP", "STUD", "RIVET"],
    "SEALING": ["GASKET", "O-RING", "SEAL", "V-RING", "U-SEAL", "PACKING", "GROMMET", "PLUG", "CAP", "BUSHING"]
}

MODELS = ["LH410", "LH514", "LH517", "TH320", "TH430", "TH551", "TH663i", "LHD1700", "TH540", "TH545", "LH203", "LH209"]

FINNISH_TERMS = {
    "PUMP": "PUMPPU",
    "ENGINE": "MOOTTORI", 
    "GASKET": "TIIVISTE",
    "HOSE": "LETKU",
    "VALVE": "VENTTIILI",
    "CYLINDER": "SYLINTERI",
    "BEARING": "LAAKERI",
    "ALTERNATOR": "LATURI",
    "STARTER": "KÄYNNISTIN",
    "TRANSMISSION": "VAIHTEISTO",
    "GEARBOX": "VAIHDELAATIKKO",
    "MIRROR": "PEILI",
    "SENSOR": "ANTURI",
    "ACCUMULATOR": "PAINEVARAAJA",
    "FILTER": "SUODATIN",
    "CONTROLLER": "OHJAIN",
    "DISPLAY": "NÄYTTÖ",
    "COMPRESSOR": "KOMPRESSORI",
    "RADIATOR": "JÄÄHDYTIN",
    "TIRE": "RENGAS",
    "CABIN": "OHJAAMO",
    "SOLENOID": "SOLENOIDI",
    "PLATE": "LEVY"
}

def generate_sku(index: int, prefix: str = "") -> str:
    """Generate SKU in Sandvik format"""
    if prefix:
        return f"{prefix}{index:08d}"
    else:
        if random.random() < 0.15:
            return f"BC{index:08d}"
        else:
            return f"{index:08d}"

def generate_old_codes(sku: str, count: int = 0) -> List[str]:
    """Generate old/alias codes"""
    if count == 0:
        count = random.choice([0, 0, 0, 1, 1, 2, 3])
    
    if count == 0:
        return []
    
    codes = []
    for _ in range(count):
        code_type = random.choice(["7F", "8X", "9A", "6G", "5H", "4K"])
        codes.append(f"{code_type}-{random.randint(1000, 9999)}")
    return codes

def generate_compatibility() -> List[str]:
    """Generate compatible models"""
    num_models = random.choice([0, 0, 1, 1, 2, 2, 3, 3, 4, 5])
    if num_models == 0:
        return []
    return random.sample(MODELS, min(num_models, len(MODELS)))

def generate_lead_time() -> int:
    """Generate realistic lead time in days"""
    weights = [30, 25, 20, 15, 5, 3, 2]  # Most parts available quickly
    days = random.choices([1, 2, 3, 5, 7, 14, 21], weights=weights)[0]
    return days

def generate_enhanced_sku_register(num_parts: int = 80000) -> List[Dict[str, Any]]:
    """Generate comprehensive SKU register"""
    parts = []
    used_skus = set()
    
    print(f"Generating {num_parts} SKU entries...")
    
    for i in range(num_parts):
        if i % 10000 == 0:
            print(f"  Generated {i} parts...")
        
        # Generate unique SKU
        sku = generate_sku(i + 1)
        while sku in used_skus:
            sku = generate_sku(random.randint(1, num_parts * 2))
        used_skus.add(sku)
        
        # Select category and part type
        category = random.choice(list(PART_CATEGORIES.keys()))
        part_type = random.choice(PART_CATEGORIES[category])
        
        # Add specifications
        specs = []
        if "BOLT" in part_type or "SCREW" in part_type:
            specs.append(f"M{random.choice([6, 8, 10, 12, 14, 16, 20])}")
        if random.random() < 0.3:
            specs.append(f"{random.choice(['HD', 'LD', 'XL', 'STD', 'ASSY'])}")
        
        # Build description
        description = part_type
        if specs:
            description = f"{part_type},{','.join(specs)}"
        
        # Add Finnish alias sometimes
        finnish_desc = None
        if part_type in FINNISH_TERMS and random.random() < 0.2:
            finnish_desc = FINNISH_TERMS[part_type]
        
        # Generate aliases/old codes
        aliases = generate_old_codes(sku)
        if finnish_desc:
            aliases.append(finnish_desc)
        
        # Generate replacements (some parts replace others)
        replacements = []
        if random.random() < 0.15:  # 15% chance of having replacements
            num_replaced = random.choice([1, 1, 2])
            for _ in range(num_replaced):
                old_sku = generate_sku(random.randint(1, max(1, i)))
                replacements.append(old_sku)
        
        # Generate compatibility
        compat = generate_compatibility()
        
        # Lead time
        lead_time = generate_lead_time()
        
        # Add some discontinued/obsolete parts
        status = "ACTIVE"
        if random.random() < 0.02:  # 2% obsolete
            status = "OBSOLETE"
            lead_time = -1
        
        part = {
            "sku": sku,
            "name": part_type,
            "description": description,
            "category": category,
            "aliases": aliases,
            "replacements": replacements,
            "compatibility": compat,
            "lead_time_days": lead_time,
            "status": status
        }
        
        parts.append(part)
    
    print(f"Generated {len(parts)} parts successfully!")
    return parts

def generate_teams_messages(count: int = 500, language: str = "EN") -> List[Dict[str, Any]]:
    """Generate synthetic Teams messages"""
    messages = []
    
    # Load existing SKUs for reference
    skus = [f"{i:08d}" for i in range(1, 50000)]
    skus.extend([f"BC{i:08d}" for i in range(1, 10000)])
    
    # Message templates
    if language == "EN":
        templates = [
            "Need replacement part for SKU {sku}, is there faster availability for next week?",
            "What's the code for this {part}? Old code missing.",
            "Lead time for {sku} {part}?",
            "hey, do we have {part} {sku} in stock? need it asap",
            "Can I get a replacment for {part} {sku}? The old one is broken",
            "What is the lead time for {part} {sku}??",
            "Is {sku} compatible with model {model}?",
            "need {part} {sku} urgently, whn can we get it?",
            "Looking for alternative to {part} {sku}, any suggestions?",
            "SKU {sku} {part} - delivery time?",
            "anyone know if we can use {sku} instead of {sku2}? both {part}",
            "Part no. {sku} - what's the replacement? Need it for {model}",
            "Hi team, can someone check availabilty for {part} {sku}? Customer waiting",
            "What {part}s are compatible with part {sku}?",
            "Old code {old_code}, what's the new SKU?",
            "{part} {sku} - is this still in production or discontinued?",
            "Need specs for {part} {sku}, also lead time pls",
            "Can we get {part} {sku} by friday? Its urgent!!!",
            "whats the part number for the {part}? customer says old number doesnt work",
            "Replacement for {part} {sku} - any cross reference?",
            "{sku} {part} available? Need {qty} pieces",
            "Part {sku} {part} - lead time and price?",
            "Is there a supersession for {sku}? {part} part",
            "{part} {sku} compatibility with {model} model?",
            "hey quick question - can i substitute {sku} {part} with {sku2}?",
            "{part} {sku}, when will it be back in stok?",
            "Looking for {part} {sku} - standard lead time?",
            "Part {sku} {part} - is this for {model} or {model2}?",
            "Can anyone cofirm if {part} {sku} fits on model {model}?",
            "Need emergency shipment for {part} {sku}, possible?",
            "{part} {sku} - any alternatives if not available?",
            "whats the lead time on {part} {sku}?? client asking",
            "{sku} {part} - is this a direct replacement for older model?",
            "{part} {sku} stock status? need for repair job",
            "Part number {sku} {part} - estimated delivery?",
            "Can someone help? Looking for {part} part, maybe {sku}?",
            "{part} {sku} - what machines is this compatible with?",
            "need {sku} {part} + {sku2} {part2}. available?",
            "{part} {sku} replacement - where can I find it in system?",
            "Anyone know lead time for {part} {sku}? Customer needs {qty}pcs"
        ]
        
        parts = ["PUMP", "GASKET", "FILTER", "BEARING", "ENGINE", "VALVE", "CYLINDER", "HOSE", 
                "ALTERNATOR", "STARTER", "RADIATOR", "TRANSMISSION", "GEARBOX", "O-RING", 
                "SENSOR", "MIRROR", "TIRE", "BOLT", "CONTROLLER", "DISPLAY"]
        
    else:  # Finnish
        templates = [
            "Tarvitaan korvaava osa SKU {sku}:lle, onko nopeampi saatavuus ensi viikolle?",
            "Mikä koodi tälle {part}? Vanha koodi puuttuu.",
            "Lead time tälle {sku} {part}?",
            "hei, onko {part} {sku} varastossa? tarvitaan asap",
            "Voisko saada korvaavan {part} {sku}? vanha on rikki",
            "Mikä on toimitusaika {part} {sku}??",
            "Onko {sku} yhteensopiva {model} mallin kanssa?",
            "tarvitaan {part} {sku} kiireellä, millon saadaan?",
            "Etsitään vaihtoehtoa {part} {sku}:lle, ehdotuksia?",
            "SKU {sku} {part} - toimitusaika?",
            "tietääkö kukaan voiko {sku} käyttää {sku2}:n sijaan? molemmat {part}",
            "Osanro {sku} - mikä korvaava? Tarvitaan {model}:ään",
            "Moi porukka, voisko joku tarkastaa saatavuuden {part} {sku}? Asiakas odottaa",
            "Mitkä {part} sopii osaan {sku}?",
            "Vanha koodi {old_code}, mikä uus SKU?",
            "{part} {sku} - onko tää vielä tuotannossa vai poistunut?",
            "Tarvitaan speksit {part} {sku}, myös toimitusaika kiitos",
            "Saadaanko {part} {sku} perjantaiksi? On kiire!!!",
            "mikä on {part} osanumero? asiakas sanoo et vanha numero ei toimi",
            "Korvaava {part} {sku} - joku ristiviite?",
            "{sku} {part} saatavilla? tarvitaan {qty}kpl",
            "Osa {sku} {part} - toimitusaika ja hinta?",
            "Onko korvike {sku}:lle? {part} osa",
            "{part} {sku} yhteensopivuus {model} mallin kans?",
            "hei pika kysymys - voiks korvata {sku} {part} {sku2}:llä?",
            "{part} {sku}, koska takas varastoon?",
            "Etsitään {part} {sku} - normaali toimitusaika?",
            "Osa {sku} {part} - onko tää {model} vai {model2}?",
            "Voiks joku vahvistaa sopiiko {part} {sku} {model} malliin?",
            "Tarvitaan hätätoimitus {part} {sku}, mahdollista?",
            "{part} {sku} - vaihtoehtosia jos ei saatavilla?",
            "mikä lead time {part} {sku}?? asiakas kysyy",
            "{sku} {part} - onko tää suora korvaava vanhalle mallille?",
            "{part} {sku} varastotilanne? tarvitaan korjaushommaan",
            "Osanumero {sku} {part} - arvioitu toimitus?",
            "Voisko joku auttaa? Etsitään {part} osaa, ehkä {sku}?",
            "{part} {sku} - mihin koneisiin sopii?",
            "tarvitaan {sku} {part} + {sku2} {part2}. saatavilla?",
            "{part} {sku} korvaava - mistä löytyy järjestelmästä?",
            "Joku tietää toimitusajan {part} {sku}? Asiakas tarvii {qty}kpl"
        ]
        
        parts = ["PUMPPU", "TIIVISTE", "SUODATIN", "LAAKERI", "MOOTTORI", "VENTTIILI", "SYLINTERI", 
                "LETKU", "LATURI", "KÄYNNISTIN", "JÄÄHDYTIN", "VAIHTEISTO", "VAIHDELAATIKKO", 
                "O-RENGAS", "ANTURI", "PEILI", "RENGAS", "PULTTI", "OHJAIN", "NÄYTTÖ"]
    
    query_types = ["replacement", "availability", "lead_time", "compatibility", "part_identification"]
    
    print(f"Generating {count} {language} messages...")
    
    for i in range(count):
        template = random.choice(templates)
        
        # Fill template
        sku = random.choice(skus)
        sku2 = random.choice(skus)
        part = random.choice(parts)
        part2 = random.choice(parts)
        model = random.choice(MODELS)
        model2 = random.choice(MODELS)
        old_code = f"{random.choice(['7F', '8X', '9A'])}-{random.randint(1000, 9999)}"
        qty = random.choice([1, 2, 3, 4, 5, 10])
        
        message = template.format(
            sku=sku,
            sku2=sku2,
            part=part,
            part2=part2,
            model=model,
            model2=model2,
            old_code=old_code,
            qty=qty
        )
        
        # Add typos randomly
        has_typo = random.random() < 0.15
        if has_typo:
            typo_words = {
                "replacement": "replacment",
                "availability": "availabilty",
                "when": "whn",
                "stock": "stok",
                "confirm": "cofirm",
                "Its": "Its",
                "toimitusaika": "toimitusaik",
                "saatavuus": "saatavuuus"
            }
            for correct, typo in typo_words.items():
                if correct in message and random.random() < 0.3:
                    message = message.replace(correct, typo, 1)
                    break
        
        # Determine query type
        query_type = "general"
        if "replacement" in message.lower() or "korvaava" in message.lower():
            query_type = "replacement"
        elif "available" in message.lower() or "stock" in message.lower() or "saatavilla" in message.lower():
            query_type = "availability"
        elif "lead time" in message.lower() or "toimitusaika" in message.lower():
            query_type = "lead_time"
        elif "compatible" in message.lower() or "yhteensopiv" in message.lower():
            query_type = "compatibility"
        elif "what's the code" in message.lower() or "mikä koodi" in message.lower():
            query_type = "part_identification"
        
        # Extract SKU if present
        referenced_sku = None
        import re
        sku_pattern = r'\b(BC\d{8}|\d{8})\b'
        matches = re.findall(sku_pattern, message)
        if matches:
            referenced_sku = matches[0]
        
        timestamp = datetime(2025, 11, 1) + timedelta(
            days=random.randint(0, 20),
            hours=random.randint(8, 17),
            minutes=random.randint(0, 59)
        )
        
        msg = {
            "message_id": f"msg_{language.lower()}_{i+1:04d}",
            "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "message": message,
            "query_type": query_type,
            "referenced_sku": referenced_sku,
            "has_typo": has_typo
        }
        
        messages.append(msg)
    
    # Sort by timestamp
    messages.sort(key=lambda x: x["timestamp"])
    
    print(f"Generated {len(messages)} {language} messages!")
    return messages

if __name__ == "__main__":
    import os
    
    # Create output directory
    output_dir = "/home/erdospeet/Desktop/sandvik/SINCE-AI-SANDVIK-CHALLENGE/test"
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("SANDVIK SYNTHETIC DATA GENERATOR")
    print("=" * 60)
    
    # Generate enhanced SKU register
    print("\n1. Generating Enhanced SKU Register...")
    sku_data = generate_enhanced_sku_register(80000)
    
    # Save as CSV
    csv_path = os.path.join(output_dir, "sku_register_full.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'sku', 'name', 'description', 'category', 'aliases', 
            'replacements', 'compatibility', 'lead_time_days', 'status'
        ])
        writer.writeheader()
        for part in sku_data:
            row = part.copy()
            row['aliases'] = '|'.join(row['aliases']) if row['aliases'] else ''
            row['replacements'] = '|'.join(row['replacements']) if row['replacements'] else ''
            row['compatibility'] = '|'.join(row['compatibility']) if row['compatibility'] else ''
            writer.writerow(row)
    
    print(f"   Saved CSV: {csv_path}")
    
    # Save as JSON
    json_path = os.path.join(output_dir, "sku_register_full.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(sku_data, f, indent=2, ensure_ascii=False)
    
    print(f"   Saved JSON: {json_path}")
    
    # Generate Teams messages
    print("\n2. Generating English Teams Messages...")
    en_messages = generate_teams_messages(500, "EN")
    en_path = os.path.join(output_dir, "teams_messages_EN_extended.json")
    with open(en_path, 'w', encoding='utf-8') as f:
        json.dump(en_messages, f, indent=2, ensure_ascii=False)
    print(f"   Saved: {en_path}")
    
    print("\n3. Generating Finnish Teams Messages...")
    fi_messages = generate_teams_messages(500, "FI")
    fi_path = os.path.join(output_dir, "teams_messages_FI_extended.json")
    with open(fi_path, 'w', encoding='utf-8') as f:
        json.dump(fi_messages, f, indent=2, ensure_ascii=False)
    print(f"   Saved: {fi_path}")
    
    # Generate edge cases
    print("\n4. Generating Edge Case Test Set...")
    edge_cases = [
        {
            "message_id": "edge_001",
            "message": "neeeed PRTS for TH663i - old code 7F-1123 doesnt work anymore!!!!",
            "query_type": "part_identification",
            "notes": "Multiple typos, excessive punctuation, old code reference"
        },
        {
            "message_id": "edge_002",
            "message": "BC0000493 or BC00000493 or BC000493?? which one is correct",
            "query_type": "part_identification",
            "notes": "Multiple SKU formats, confusion"
        },
        {
            "message_id": "edge_003",
            "message": "pump",
            "query_type": "part_identification",
            "notes": "Single word query"
        },
        {
            "message_id": "edge_004",
            "message": "Do we have any 5mm bolts M12 thread for the LH517 front assembly? Customer needs 50 pieces by tomorrow morning, very urgent!!!",
            "query_type": "availability",
            "notes": "Complex query with specifications, quantity, deadline"
        },
        {
            "message_id": "edge_005",
            "message": "tiiviste gasket seal O-ring for hydraulic cylinder LH410",
            "query_type": "part_identification",
            "notes": "Mixed languages, multiple synonyms"
        },
        {
            "message_id": "edge_006",
            "message": "btw anyone checked if the new shipment arrived? talking about the radiators we ordered last month",
            "query_type": "general",
            "notes": "Conversational, vague reference"
        },
        {
            "message_id": "edge_007",
            "message": "00002771",
            "query_type": "part_identification",
            "notes": "SKU only, no context"
        },
        {
            "message_id": "edge_008",
            "message": "Onko meillä stock ALTERNATOR BC00002492 and also STARTER 00002707 compatibility with model TH430??",
            "query_type": "compatibility",
            "notes": "Mixed Finnish/English, multiple parts, multiple questions"
        }
    ]
    
    edge_path = os.path.join(output_dir, "teams_messages_edge_cases.json")
    with open(edge_path, 'w', encoding='utf-8') as f:
        json.dump(edge_cases, f, indent=2, ensure_ascii=False)
    print(f"   Saved: {edge_path}")
    
    # Generate statistics
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE!")
    print("=" * 60)
    print(f"\nDataset Statistics:")
    print(f"  SKU Register:")
    print(f"    - Total parts: {len(sku_data):,}")
    print(f"    - With aliases: {sum(1 for p in sku_data if p['aliases']):,}")
    print(f"    - With replacements: {sum(1 for p in sku_data if p['replacements']):,}")
    print(f"    - With compatibility: {sum(1 for p in sku_data if p['compatibility']):,}")
    print(f"    - Obsolete parts: {sum(1 for p in sku_data if p['status'] == 'OBSOLETE'):,}")
    print(f"\n  Teams Messages:")
    print(f"    - English: {len(en_messages):,}")
    print(f"    - Finnish: {len(fi_messages):,}")
    print(f"    - Edge cases: {len(edge_cases):,}")
    print(f"    - Total: {len(en_messages) + len(fi_messages) + len(edge_cases):,}")
    
    print(f"\n  Files created in: {output_dir}")
    print("=" * 60)

