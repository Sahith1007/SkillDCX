"use client";

import { useState } from "react";

export default function VerifyCertificate() {
  const [hash, setHash] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  const handleVerify = async () => {
    setError("");
    setData(null);
    if (!hash) {
      setError("Please enter an IPFS hash");
      return;
    }

    try {
      const res = await fetch(`http://127.0.0.1:8000/verify/certificate/${hash}`);
      if (!res.ok) throw new Error("Invalid or not found");

      const json = await res.json();
      setData(json.data);
    } catch (err) {
      setError("Certificate not found or invalid");
    }
  };

  return (
    <div className="flex flex-col items-center p-8">
      <h1 className="text-3xl font-bold mb-6">Verify Certificate</h1>
      <div className="flex space-x-2 mb-4">
        <input
          type="text"
          value={hash}
          onChange={(e) => setHash(e.target.value)}
          placeholder="Enter IPFS hash"
          className="border rounded-xl px-4 py-2 w-96"
        />
        <button
          onClick={handleVerify}
          className="bg-blue-600 text-white rounded-xl px-6 py-2 hover:bg-blue-700"
        >
          Verify
        </button>
      </div>

      {error && <p className="text-red-500 mt-2">{error}</p>}

      {data && (
        <div className="bg-gray-100 p-6 rounded-xl shadow-md mt-6 w-[500px]">
          <h2 className="text-xl font-semibold mb-2">Certificate Details</h2>
          <pre className="whitespace-pre-wrap">{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
