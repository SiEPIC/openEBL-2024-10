import gdsfactory as gf
import ubcpdk
import numpy as np

@gf.cell
def variable_delta_mzi(splitter=ubcpdk.components.ebeam_y_1550(),
                       delta_length: float = 0,
                       length_x: float = 37,
                       length_y: float = 15,
                       **kwargs) -> gf.Component:
    """Create variable delta L MZI"""
    mzi = ubcpdk.components.mzi(splitter,
                             delta_length=delta_length,
                             length_x=length_x,
                             length_y=length_y,
                             **kwargs)
    
    return gf.add_pins.add_pins_container(mzi, layer=ubcpdk.LAYER.PORT)

@gf.cell
def variable_delta_mzi_with_gc(delta_lengths: list[float] = [0]) -> gf.Component:
    """Create variabable delta L MZIs with gratings couplers"""
    cell = gf.Component()

    cell << gf.components.rectangle(size=(605, 410), layer=(99, 0))

    cum_lengths = np.cumsum(delta_lengths[1::2]) / 2
    cum_lengths -= cum_lengths[0]

    for i, delta_length in enumerate(delta_lengths):
        single_circuit = gf.Component(name=f"mzi_circuit_{i}")

        x_offset = cum_lengths[i // 2] + 70 * (i // 2)
        y_offset = 2 * 127 * (i % 2)

        mzi = single_circuit << variable_delta_mzi(delta_length=delta_length)

        mzi.drotate(90)
        mzi.dy += y_offset + 31
        mzi.dx += x_offset + 50

        gc = single_circuit << gf.components.grating_coupler_array(grating_coupler=ubcpdk.components.gc_te1550(),
                                                        n=2,)
        gc.drotate(angle=-90)
        gc.dy += y_offset + 77
        gc.dx += x_offset + 37

        gf.routing.route_bundle(single_circuit, ports1=mzi.ports, ports2=list(gc.ports)[::-1])

        single_circuit.add_label(text=f"opt_in_TE_1550_device_LouisBelangerSansoucy_MZI{i}",
                       position=gc.ports[0].dcenter, layer=ubcpdk.LAYER.TEXT)
        
        cell.add_port(f'o{i * 2}', port=gc.ports['o0'])
        cell.add_port(f'o{i * 2 + 1}', port=gc.ports['o1'])
        
        cell << single_circuit
    
    #port_layers = (ubcpdk.LAYER.PORT, ubcpdk.LAYER.PORTE)
    #extract = cell.extract(layers=port_layers)
    #_ = extract.remove_layers(layers=port_layers)

    return cell

if __name__ == "__main__":
    variable_delta_mzi_with_gc(delta_lengths=list(np.linspace(0, 112.5, 10))).write_gds("./submissions/EBeam_lbelangers2.gds")