"use client";

// app/page.tsx
import styles from "./page.module.css";

export default function Home() {
  return (
    <main className={styles.main}>
      {/* سایدبار سمت چپ */}
      <aside className={styles.sidebar}>
        <div className={styles.sidebarSection}>
          <h2 className={styles.sidebarTitle}>اطلاعات تماس</h2>
          <p>📧 Sadaf.biglarian02@gmail.com</p>
          <p>📱 09113281488</p>
          <p>
            💼 لینکدین:{" "}
            <a href="#" target="_blank" rel="noreferrer">
              لینک پروفایل
            </a>
          </p>
          <p>
            💻 گیت‌هاب:{" "}
            <a href="#" target="_blank" rel="noreferrer">
              لینک گیت‌هاب
            </a>
          </p>
          <p>مازندران، کلاردشت </p>
        </div>

        <div className={styles.sidebarSection}>
          <h2 className={styles.sidebarTitle}>مهارت‌های کلیدی</h2>
          <ul>
            <li>Python</li>
            <li>JavaScript / Next.js</li>
            <li>SQL</li>
            <li>Git & GitHub</li>
          </ul>
        </div>

        <div className={styles.sidebarSection}>
          <h2 className={styles.sidebarTitle}>مدارک</h2>
          <ul>
            <li>کارشناسی کامپیوتر – 1400</li>
            <li>جاوا اسکریپت</li>
          </ul>
        </div>
        <div>
          <button className={styles.downloadBtn} onClick={() => window.print()}>
            دانلود این صفحه (PDF)
          </button>
        </div>
        {/* <div>
          <a href="/resume.pdf" download className={styles.downloadBtn}>
            دانلود رزومه (PDF)
          </a>
        </div> */}
      </aside>

      {/* بخش اصلی محتوا */}
      <div className={styles.contentArea}>
        <header className={styles.header}>
          <div className={styles.headerText}>
            <h1>صدف بیگ لریان </h1>
            <h2>Network Security Engineer</h2>
            <p>
              متخصص طراحی، پیاده‌سازی و امن‌سازی زیرساخت‌های شبکه، فایروال، VPN
              و مانیتورینگ امنیتی
            </p>
          </div>

          <div className={styles.profileBox}>
            <span>محل عکس پروفایل</span>
          </div>
        </header>

        <section className={styles.section}>
          <h3>درباره من</h3>
          <p>
            مهندس امنیت شبکه با تجربه در طراحی و پیاده‌سازی زیرساخت‌های امن،
            پیکربندی فایروال‌ها، راه‌اندازی VPNهای سازمانی و مانیتورینگ
            رویدادهای امنیتی. مسلط به مفاهیم روتینگ، سوئیچینگ، پروتکل‌های امنیتی
            و تست نفوذ پایه روی شبکه. سابقه کار با تیم‌های زیرساخت و توسعه برای
            شناسایی و رفع آسیب‌پذیری‌ها و پیاده‌سازی Best Practiceهای امنیتی.
            علاقه‌مند به یادگیری مداوم و مستندسازی و آموزش مفاهیم امنیت به اعضای
            تیم.{" "}
          </p>
        </section>

        <section className={styles.section}>
          <h3>تجربه کاری و پروژه‌ها</h3>
          <ul>
            <li>
              توسعه پنل مدیریت برای یک فروشگاه آنلاین با استفاده از next.js.
            </li>
          </ul>
        </section>

        <section className={styles.section}>
          <h3>علایق و فعالیت‌ها</h3>
          <ul>
            <li>شرکت در مسابقات برنامه‌نویسی و حل مسئله</li>
            <li>تولید محتوا آموزشی </li>
          </ul>
        </section>
      </div>
    </main>
  );
}
