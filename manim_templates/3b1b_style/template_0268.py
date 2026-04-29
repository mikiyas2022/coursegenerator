"""
Template 0268 — VECTOR: angle_t.get_ ROSE_COLOR
"""
class SceneTemplate(AmharicEduScene):
    def construct(self):
        setup_scene(self)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_0>") as tracker:
            axes = branded_axes([-3,3,1],[-3,3,1]).scale(0.55)
            axes.move_to(ORIGIN)
            self.play(Create(axes), run_time=tracker.duration*0.2)
            angle_t = ValueTracker(0)
            vec = always_redraw(lambda: Arrow(axes.c2p(0,0), axes.c2p(2*np.cos(angle_t.get_value()+PI/2), 2*np.sin(angle_t.get_value()+PI/2)), buff=0, color=ROSE_COLOR, stroke_width=5, max_tip_length_to_length_ratio=0.15))
            self.add(vec)
            self.play(angle_t.animate.set_value(PI), run_time=tracker.duration*0.55, rate_func=smooth)
            self.play(Indicate(vec, color=STAR_YELLOW), run_time=tracker.duration*0.15)

        self.clear()
        with self.voiceover(text="<NARRATION_PLACEHOLDER_1>") as tracker:
            obj = latin_text("<NARRATION_PLACEHOLDER_1>", font_size=FONT_SIZE_BODY, color=ROSE_COLOR)
            obj.move_to(ORIGIN)
            clamp_to_screen(obj)
            self.play(Write(obj), run_time=tracker.duration*0.5)
            self.play(Circumscribe(obj, color=STAR_YELLOW, time_width=2), run_time=tracker.duration*0.3)
            self.wait(tracker.duration*0.1)

        self.wait(0.5)
