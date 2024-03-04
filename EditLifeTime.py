try:
    import LtMAO.binfile as bin
    from sys import argv

    if len(argv) != 2:
        print("Plz drag and drop a .bin to this app, dont try to open it!")
        input("")
        exit()

    def compute_hash(s: str):
        if s.startswith("0x"):
            return s.removeprefix("0x")
        
        h = 0x811c9dc5 
        for b in s.encode('ascii').lower(): 
            h = ((h ^ b) * 0x01000193) % 0x100000000 
        return f"{h:08x}"
    
    CONSTANTS = {
        "VfxSystemDefinitionData": compute_hash("VfxSystemDefinitionData"),
        "ComplexEmitterDefinitionData": compute_hash("ComplexEmitterDefinitionData"),
        "ParticleLifetime": compute_hash("ParticleLifetime"),
        "ConstantValue": compute_hash("ConstantValue"),
        "Dynamics": compute_hash("Dynamics"),
        "ProbabilityTables": compute_hash("ProbabilityTables"),
        "KeyValues": compute_hash("KeyValues"),
        "Values": compute_hash("Values"),
        "EmitterName": compute_hash("EmitterName")
    }
    
    bin_file = bin.BIN()
    bin_file.read(argv[1])
    
    amount_to_multiply = float(input("Value to multiply: "))
    ans = input("Want to filter by VfxSystemDefinitionData? (y/yes) ").lower()
    emitters = []
    target = None
    if ans in ["y", "yes"]:
        target = compute_hash(input("Type the name of the VfxSystem, if is hashed make sure to start with 0x: ").lower())
        ans = input("Want to also filter by the emitters name? (y/yes) ").lower()
        if ans in ["y", "yes"]:
            emitters_input = input("Type the emitter names (use a comma to multiple ones [example: distort,wave]) ").lower()
            if ',' in emitters_input: emitters = emitters_input.split(",")
            else: emitters.append(emitters_input)
    else:
        print("Not using any filter then uwu")

    def change_emitter(emitter):
        for x in emitter.data:
            if x.hash == CONSTANTS["ParticleLifetime"]:
                for y in x.data:
                    if y.hash == CONSTANTS["ConstantValue"]:
                        y.data = y.data * amount_to_multiply
                    elif y.hash == CONSTANTS["Dynamics"]:
                        for z in y.data:
                            if z.hash == CONSTANTS["ProbabilityTables"]:
                                for ProbabilityTableData in z.data:
                                    for shit in ProbabilityTableData.data:
                                        if shit.hash == CONSTANTS["KeyValues"]:
                                            shit.data = [x*amount_to_multiply for x in shit.data]
                            elif z.hash == CONSTANTS["Values"]:
                                z.data = [x*amount_to_multiply for x in z.data]

    for entry in bin_file.entries:
        if entry.type == CONSTANTS['VfxSystemDefinitionData']:
            if entry.hash == target or not target:
                for data in entry.data:
                    if data.hash == CONSTANTS["ComplexEmitterDefinitionData"]:
                        for emitter in data.data:
                            if not emitters: change_emitter(emitter)
                            else:
                                for x in emitter.data:
                                    if x.hash == CONSTANTS["EmitterName"]:
                                        if x.data.lower() in emitters:
                                            change_emitter(emitter)
    bin_file.write(argv[1])


except Exception as e:
    print(e, '\n')
    input('Something went wrong lol uwu')