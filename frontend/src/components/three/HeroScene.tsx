"use client";
import { Canvas, useFrame } from "@react-three/fiber";
import { Grid, Float, Environment } from "@react-three/drei";
import { useRef } from "react";
import * as THREE from "three";

function DataMonolith() {
  const meshRef = useRef<THREE.Mesh>(null);
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.getElapsedTime() * 0.15;
      meshRef.current.rotation.x = Math.sin(state.clock.getElapsedTime() * 0.2) * 0.1;
    }
  });

  return (
    <Float speed={1.5} rotationIntensity={0.2} floatIntensity={0.5}>
      <group position={[0, 1.5, 0]}>
        {/* Outer Wireframe Shell */}
        <mesh ref={meshRef}>
          <octahedronGeometry args={[1.5, 0]} />
          <meshStandardMaterial 
            color="#050505" 
            emissive="#00E5FF" 
            emissiveIntensity={0.2} 
            roughness={0.1} 
            metalness={1} 
            wireframe
          />
        </mesh>
        {/* Inner Glowing Core */}
        <mesh scale={0.7}>
          <octahedronGeometry args={[1, 0]} />
          <meshStandardMaterial 
            color="#00E5FF" 
            emissive="#00E5FF" 
            emissiveIntensity={3} 
            toneMapped={false} 
          />
        </mesh>
      </group>
    </Float>
  );
}

export default function HeroScene() {
  return (
    <Canvas 
      shadows 
      camera={{ position: [0, 4, 12], fov: 45 }}
      gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
    >
      <color attach="background" args={["#030303"]} />
      <fog attach="fog" args={["#030303", 10, 25]} />
      
      {/* Cinematic Lighting */}
      <ambientLight intensity={0.1} />
      <directionalLight position={[5, 8, 5]} intensity={0.8} color="#ffffff" castShadow />
      <pointLight position={[0, 2, 0]} intensity={5} color="#00E5FF" distance={15} decay={2} />
      <pointLight position={[-5, -2, -5]} intensity={2} color="#ff0055" distance={10} decay={2} />

      <DataMonolith />
      
      {/* Infinite Premium Data Grid */}
      <Grid 
        position={[0, -0.5, 0]}
        args={[40, 40]}
        cellSize={0.6}
        cellThickness={0.5}
        cellColor="#1a1a1a"
        sectionSize={3}
        sectionThickness={1.2}
        sectionColor="#00E5FF"
        fadeDistance={30}
        fadeStrength={1.5}
        followCamera={false}
        infiniteGrid
      />
    </Canvas>
  );
}
