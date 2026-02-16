import tkinter as tk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


df = pd.read_csv(r"C:\Users\VAIDEHI\OneDrive\student_performance_3_exams_detailed.csv")
subjects = ["Math", "Science", "English", "History", "Art"]
exam_cols = [f"{s}_Exam{i}" for s in subjects for i in range(1, 4)]


df["Average"] = df[exam_cols].mean(axis=1)
df["GPA"] = (df["Average"] / 100) * 10
df["Percentile"] = df["GPA"].rank(pct=True) * 100
df["At_Risk"] = (df["GPA"] < 4.0) | (df["Percentile"] < 25)

root = tk.Tk()
root.title("Academic Performance Analytics – BSc CS")
root.geometry("1000x700") 
root.configure(bg="#f4f6f7")

style = ttk.Style()
style.configure("TButton", font=("Segoe UI", 11, "bold"))
style.configure("Treeview", font=("Segoe UI", 11), rowheight=30)
style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))

text = tk.Text(root, font=("Segoe UI", 12), bg="white", relief="flat", padx=20, pady=20)
text.pack(expand=True, fill="both", padx=25, pady=(25, 10))

text.tag_config("title", font=("Segoe UI", 18, "bold"), foreground="#2c3e50")
text.tag_config("crit", font=("Segoe UI", 13, "bold"), foreground="#c0392b")
text.tag_config("header", font=("Segoe UI", 12, "bold"))

def clear():
    for child in root.winfo_children():
        if isinstance(child, (ttk.Treeview, ttk.Combobox, tk.Label)) and child.winfo_y() < 600:
            child.destroy()
    text.pack(expand=True, fill="both", padx=25, pady=(25, 10))
    text.delete("1.0", tk.END)


def show_summary():
    clear()
    text.insert(tk.END, "OVERALL CLASS SUMMARY\n\n", "title")
    text.insert(tk.END, f"Total Students: {len(df)}\n\n")
    text.insert(tk.END, f"Class Average GPA: {df['GPA'].mean():.2f}\n\n")
    text.insert(tk.END, f"At-Risk Students: {df['At_Risk'].sum()}\n", "crit")
    
    plt.figure(figsize=(6,4))
    exam_avgs = [df[[f"{s}_Exam{i}" for s in subjects]].mean().mean() for i in range(1, 4)]
    plt.plot(["Exam 1", "Exam 2", "Exam 3"], exam_avgs, marker='o', color='#3498db', linewidth=3)
    plt.title("General Exam Progression", fontsize=14)
    plt.show()

def show_top_10():
    clear()
    text.insert(tk.END, "TOP 10 ACADEMIC ACHIEVERS\n\n", "title")
    top_df = df.nlargest(10, 'GPA')[["Student_ID", "GPA", "Percentile"]]
    text.insert(tk.END, top_df.to_string(index=False, justify='center'))

def show_at_risk():
    clear()
    text.insert(tk.END, "AT-RISK IDENTIFICATION\n\n", "title")
    text.insert(tk.END, "Criteria:\n", "header")
    text.insert(tk.END, "• Absolute: GPA < 4.0\n• Relative: Percentile < 25th\n\n", "crit")
    
    tk.Label(root, text="Filter by Subject:", bg="#f4f6f7", font=("Segoe UI", 11)).place(x=25, y=165)
    sub_var = tk.StringVar(value="Overall")
    drop = ttk.Combobox(root, textvariable=sub_var, values=["Overall"] + subjects, state="readonly", font=("Segoe UI", 11))
    drop.place(x=160, y=165, width=150)
    
    tree_frame = tk.Frame(root)
    tree_frame.place(x=25, y=210, width=950, height=380)
    
    def update_table(event=None):
        for child in tree_frame.winfo_children(): child.destroy()
        selected = sub_var.get()
        if selected == "Overall":
            cols = ("Student_ID", "GPA", "Percentile")
            display_df = df[df["At_Risk"]][["Student_ID", "GPA", "Percentile"]]
        else:
            cols = ("Student_ID", "Exam_1", "Exam_2", "Exam_3")
            subj_cols = ["Student_ID", f"{selected}_Exam1", f"{selected}_Exam2", f"{selected}_Exam3"]
            display_df = df[df["At_Risk"]][subj_cols]

        tree = ttk.Treeview(tree_frame, columns=cols, show="headings")
        for c in cols: 
            tree.heading(c, text=c)
            tree.column(c, width=150, anchor="center")
        for _, row in display_df.round(2).iterrows(): tree.insert("", tk.END, values=list(row))
        tree.pack(fill="both", expand=True)

    drop.bind("<<ComboboxSelected>>", update_table)
    update_table()
    text.pack_forget()


def show_gpa_hist():
    plt.figure(figsize=(7, 5))
    sns.histplot(df["GPA"], bins=10, kde=True, color="#27ae60")
    plt.title("GPA Distribution (Line = Density Curve)", fontsize=14)
    plt.xlabel("GPA", fontsize=12)
    plt.ylabel("Frequency", fontsize=12)
    plt.show()

def show_heatmap():
    avg_sub = {s: df[[f"{s}_Exam1", f"{s}_Exam2", f"{s}_Exam3"]].mean(axis=1) for s in subjects}
    plt.figure(figsize=(9, 7))
    sns.heatmap(pd.DataFrame(avg_sub).corr(), annot=True, cmap="coolwarm", annot_kws={"size": 12})
    plt.title("Subject Correlation Heatmap", fontsize=14)
    plt.show()

def show_boxplots():
    long_df = df.melt(id_vars=["Student_ID"], value_vars=exam_cols, var_name="Subject_Exam", value_name="Marks")
    long_df["Subject"] = long_df["Subject_Exam"].apply(lambda x: x.split("_")[0])
    plt.figure(figsize=(10, 6))
    sns.boxplot(x="Subject", y="Marks", data=long_df, palette="Set3")
    plt.title("Subject-wise Marks Distribution", fontsize=14)
    plt.show()

btn_frame = tk.Frame(root, bg="#d5d8dc", pady=15)
btn_frame.pack(side="bottom", fill="x")

btns = [
    ("Summary", show_summary), ("Top 10", show_top_10), 
    ("At-Risk", show_at_risk), ("GPA Hist", show_gpa_hist),
    ("Correlation", show_heatmap), ("Box Plots", show_boxplots)
]

for txt_btn, cmd in btns:
    ttk.Button(btn_frame, text=txt_btn, command=cmd).pack(side="left", padx=8, expand=True)

show_summary()
root.mainloop()
