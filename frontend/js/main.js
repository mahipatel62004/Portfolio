// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------
const API_BASE_URL = window.PORTFOLIO_API_BASE_URL || "http://localhost:5000/api";

// ---------------------------------------------------------------------------
// Footer year
// ---------------------------------------------------------------------------
document.getElementById("year").textContent = new Date().getFullYear();

// ---------------------------------------------------------------------------
// Toasts
// ---------------------------------------------------------------------------
function showToast(message, type = "success", duration = 5000) {
  const stack = document.getElementById("toast-stack");
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.setAttribute("role", "status");
  toast.textContent = message;
  stack.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.25s ease";
    setTimeout(() => toast.remove(), 250);
  }, duration);
}

// ---------------------------------------------------------------------------
// Frontend validation (mirrors backend rules)
// ---------------------------------------------------------------------------
const rules = {
  fullName: (v) => (v.trim().length >= 2 ? "" : "Full name must be at least 2 characters."),
  email: (v) => (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim()) ? "" : "Enter a valid email address."),
  company: () => "",
  subject: (v) => (v.trim().length >= 3 ? "" : "Subject must be at least 3 characters."),
  message: (v) => (v.trim().length >= 10 ? "" : "Message must be at least 10 characters."),
};

function validateField(name, value) {
  const rule = rules[name];
  return rule ? rule(value) : "";
}

function setFieldError(name, message) {
  const field = document.getElementById(name).closest(".field");
  const errorEl = document.querySelector(`[data-error-for="${name}"]`);
  if (message) {
    field.classList.add("has-error");
    errorEl.textContent = message;
  } else {
    field.classList.remove("has-error");
    errorEl.textContent = "";
  }
}

// ---------------------------------------------------------------------------
// Form submission
// ---------------------------------------------------------------------------
const form = document.getElementById("inquiry-form");
const submitBtn = document.getElementById("submit-btn");

["fullName", "email", "subject", "message"].forEach((name) => {
  document.getElementById(name).addEventListener("blur", (e) => {
    setFieldError(name, validateField(name, e.target.value));
  });
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const data = {
    fullName: form.fullName.value.trim(),
    email: form.email.value.trim(),
    company: form.company.value.trim(),
    subject: form.subject.value.trim(),
    message: form.message.value.trim(),
    website: form.website.value, // honeypot - stays empty for real users
  };

  // Client-side validation pass
  let hasError = false;
  ["fullName", "email", "subject", "message"].forEach((name) => {
    const msg = validateField(name, data[name]);
    setFieldError(name, msg);
    if (msg) hasError = true;
  });

  if (hasError) {
    showToast("Please fix the highlighted fields.", "error");
    return;
  }

  setLoading(true);

  try {
    const res = await fetch(`${API_BASE_URL}/inquiries`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const result = await res.json().catch(() => ({}));

    if (!res.ok || !result.success) {
      // Surface field-level errors from the backend if present
      if (result.errors) {
        Object.entries(result.errors).forEach(([field, msgs]) => {
          setFieldError(field, Array.isArray(msgs) ? msgs[0] : String(msgs));
        });
      }
      showToast(result.message || "Something went wrong. Please try again.", "error");
      return;
    }

    showToast(result.message || "Thanks! Your inquiry has been sent.", "success");
    form.reset();
  } catch (err) {
    showToast("Thanks! Your inquiry has been sent.", "error");
  } finally {
    setLoading(false);
  }
});

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  submitBtn.classList.toggle("is-loading", isLoading);
  submitBtn.querySelector(".btn-text").textContent = isLoading ? "Sending…" : "Send Inquiry";
}

// ---------------------------------------------------------------------------
// Scroll-reveal (subtle, respects reduced motion)
// ---------------------------------------------------------------------------
if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches && "IntersectionObserver" in window) {
  const revealTargets = document.querySelectorAll("section .container > *");
  revealTargets.forEach((el) => {
    el.style.opacity = "0";
    el.style.transform = "translateY(16px)";
    el.style.transition = "opacity 0.5s ease, transform 0.5s ease";
  });
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = "1";
          entry.target.style.transform = "translateY(0)";
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1 }
  );
  revealTargets.forEach((el) => observer.observe(el));
}
