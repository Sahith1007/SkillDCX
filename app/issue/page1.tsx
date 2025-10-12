"use client";
import { useCertificates } from "@/hooks/usecertificates";

export default function Page1() {
  const { certificates, loading, error } = useCertificates();

  if (loading) return <p>Loading certificates...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div>
      <h1>Issued Certificates</h1>
      {certificates.length === 0 ? (
        <p>No certificates found</p>
      ) : (
        <ul>
          {certificates.map((cert) => (
            <li key={cert.id}>
              {cert.student_id} — {cert.course} ({cert.grade})<br />
              <a
                href={`https://ipfs.io/ipfs/${cert.ipfs_hash}`}
                target="_blank"
                rel="noopener noreferrer"
              >
                View on IPFS
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
