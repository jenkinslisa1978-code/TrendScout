import { useState, useRef, useEffect } from 'react';

/**
 * Lazy-loaded image with blur placeholder, error fallback, and IntersectionObserver.
 * Replaces <img> for better performance on image-heavy pages.
 */
export default function LazyImage({ src, alt, className = '', fallback, ...rest }) {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);
  const [inView, setInView] = useState(false);
  const imgRef = useRef(null);

  useEffect(() => {
    const el = imgRef.current;
    if (!el) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setInView(true);
          observer.disconnect();
        }
      },
      { rootMargin: '200px' }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  const handleError = () => {
    setError(true);
    setLoaded(true);
  };

  return (
    <div ref={imgRef} className={`relative overflow-hidden ${className}`} {...rest}>
      {/* Placeholder */}
      {!loaded && (
        <div className="absolute inset-0 bg-slate-100 animate-pulse" />
      )}

      {inView && !error && (
        <img
          src={src}
          alt={alt || ''}
          loading="lazy"
          decoding="async"
          onLoad={() => setLoaded(true)}
          onError={handleError}
          className={`w-full h-full object-cover transition-opacity duration-300 ${loaded ? 'opacity-100' : 'opacity-0'}`}
        />
      )}

      {error && (
        fallback || (
          <div className="absolute inset-0 bg-slate-100 flex items-center justify-center">
            <span className="text-xs text-slate-400">No image</span>
          </div>
        )
      )}
    </div>
  );
}
