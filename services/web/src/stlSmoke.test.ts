import { describe, expect, it } from "vitest";
import * as THREE from "three";
import { STLLoader } from "three/examples/jsm/loaders/STLLoader.js";

const asciiCube = `solid ascii
facet normal 0 0 1
  outer loop
    vertex 0 0 0
    vertex 1 0 0
    vertex 0 1 0
  endloop
endfacet
endsolid ascii`;

/** Smoke: STLLoader aceita mesh mínimo (uso no MeshViewport). */
describe("STL parse smoke", () => {
  it("parses ascii STL bytes", () => {
    const buf = new TextEncoder().encode(asciiCube);
    const geo = new STLLoader().parse(buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength));
    geo.computeVertexNormals();
    expect(geo.attributes.position.count).toBeGreaterThanOrEqual(3);
    expect(new THREE.Box3().setFromBufferAttribute(geo.attributes.position as THREE.BufferAttribute).isEmpty()).toBe(
      false,
    );
  });
});
