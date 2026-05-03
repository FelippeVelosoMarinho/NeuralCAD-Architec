import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { Suspense, useMemo } from "react";
import * as THREE from "three";
import { STLLoader } from "three/examples/jsm/loaders/STLLoader.js";

type Props = {
  buffer: ArrayBuffer | null;
  error: string | null;
  loading: boolean;
};

/** Viewport STL com órbita e materiais simples. */
export function MeshViewport({ buffer, error, loading }: Props) {
  const geoScale = useMemo(() => {
    if (!buffer) return null;
    const loader = new STLLoader();
    const geom = loader.parse(buffer);
    geom.computeVertexNormals();
    geom.center();
    const pos = geom.getAttribute("position") as THREE.BufferAttribute;
    const box = new THREE.Box3().setFromBufferAttribute(pos);
    const size = new THREE.Vector3();
    box.getSize(size);
    const maxDim = Math.max(size.x, size.y, size.z, 1e-6);
    const scale = 2 / maxDim;
    return { geom, scale };
  }, [buffer]);

  if (loading) return <div className="viewport-placeholder">A carregar mesh…</div>;
  if (error) return <div className="viewport-placeholder">{error}</div>;
  if (!geoScale) return <div className="viewport-placeholder">Completa um job para ver o STL.</div>;

  return (
    <div className="mesh-viewport-fill mesh-viewport-canvas">
      <Canvas camera={{ position: [2.5, 2, 2.5], fov: 50 }}>
        <color attach="background" args={["#1a1a1c"]} />
        <ambientLight intensity={0.65} />
        <directionalLight position={[6, 8, 4]} intensity={0.85} />
        <Suspense fallback={null}>
          <mesh geometry={geoScale.geom} scale={geoScale.scale}>
            <meshPhysicalMaterial color="#89b4fa" roughness={0.4} metalness={0.2} />
          </mesh>
        </Suspense>
        <OrbitControls enableDamping makeDefault />
      </Canvas>
    </div>
  );
}
